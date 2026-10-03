"""本地 calculations 工具：对教材样本做 Decimal 运算，输出公式和来源。"""
from pathlib import Path
from decimal import Decimal, localcontext, ROUND_HALF_UP
import argparse, ast, hashlib, json

ROOT=Path(__file__).resolve().parents[1]

def calculate(expression, variables):
    def visit(node):
        if isinstance(node,ast.Expression):return visit(node.body)
        if isinstance(node,ast.Name):return Decimal(variables[node.id])
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):return Decimal(str(node.value))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=visit(node.operand);return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node,ast.BinOp):
            left,right=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):return left/right
        raise ValueError('Only numbers, declared variables, + - * / and parentheses are accepted')
    with localcontext() as ctx:
        ctx.prec=40
        return visit(ast.parse(expression,mode='eval'))

def report(dataset):
    variables={}
    for name,rows in dataset['samples'].items():
        if not rows:raise ValueError('Empty task set: '+name)
        if any(type(row['passed']) is not bool or type(row['tokens']) is not int or row['tokens']<0 for row in rows):
            raise ValueError('Invalid pass/token observation')
        if len({row['id'] for row in rows})!=len(rows):raise ValueError('Duplicate sample identity')
        variables[name+'_tasks']=Decimal(len(rows))
        variables[name+'_passed']=sum((Decimal(int(row['passed'])) for row in rows),Decimal(0))
        variables[name+'_tokens']=sum((Decimal(row['tokens']) for row in rows),Decimal(0))
    assert [row['id'] for row in dataset['samples']['A']]==[row['id'] for row in dataset['samples']['B']], 'Paired task identities differ'
    for group in ['byte_examples','numeric_examples']:
        for name,value in dataset[group].items():
            if type(value) is not int or value<0:raise ValueError('Invalid numeric input: '+name)
            variables[name]=Decimal(value)
    events=dataset['event_examples']
    variables.update(C3_turn_starts=Decimal(events['C3'].count('turn-start')),C3_step_starts=Decimal(events['C3'].count('step-start')),
                     C3_attempts=Decimal(events['C3'].count('attempt')),C3_tool_calls=Decimal(events['C3'].count('tool-call')),
                     C5_message_count=Decimal(sum(kind in ('user-message','assistant-message','tool-result') for kind in events['C5'])),
                     C5_tool_calls=Decimal(events['C5'].count('tool-call')),C5_event_count=Decimal(len(events['C5'])),
                     C11_requested=Decimal(len(events['C11'])),C11_executed=Decimal(sum(kind.startswith('execution-') for kind in events['C11'])),
                     C11_succeeded=Decimal(events['C11'].count('execution-succeeded')),
                     C11_rejected=Decimal(sum(kind.endswith('-rejected') for kind in events['C11'])),
                     retry_attempt_count=Decimal(len([variables['retry_first_ms'],variables['retry_second_ms']])),
                     parallel_children_ms=max(variables['child_first_ms'],variables['child_second_ms']))
    requests={
        'A_pass_percent':('A_passed / A_tasks * 100','%'),
        'B_pass_percent':('B_passed / B_tasks * 100','%'),
        'token_reduction_percent':('(A_tokens - B_tokens) / A_tokens * 100','%'),
        'pass_drop_percentage_points':('(A_passed / A_tasks - B_passed / B_tasks) * 100','百分点'),
        'relative_gain_B_to_A_percent':('((A_passed / A_tasks) / (B_passed / B_tasks) - 1) * 100','%'),
        'A_tokens_per_pass':('A_tokens / A_passed','token / 通过任务'),
        'B_tokens_per_pass':('B_tokens / B_passed','token / 通过任务'),
        'C6_baseline_bytes':('tools_guidance + project_rules + user_request + history','字节'),
        'C6_augmented_bytes':('tools_guidance + project_rules + user_request + history + duplicate_rules','字节'),
        'C6_increase_percent':('duplicate_rules / (tools_guidance + project_rules + user_request + history) * 100','%'),
        'C8_saved_bytes':('region_before - region_after','字节'),
        'C8_reduction_percent':('(region_before - region_after) / region_before * 100','%'),
        'C8_future_saved_bytes':('(region_before - region_after) * future_requests','字节'),
        'C3_turn_count':('C3_turn_starts','turn'),
        'C3_step_count':('C3_step_starts','step'),
        'C3_attempt_count':('C3_attempts','attempt'),
        'C3_tool_call_count':('C3_tool_calls','Tool Call'),
        'C4_last_line':('read_offset + read_limit - 1','行号'),
        'C4_remaining_lines':('file_lines - (read_offset + read_limit - 1)','行'),
        'C5_messages':('C5_message_count','消息'),
        'C5_calls':('C5_tool_calls','Tool Call'),
        'C5_events':('C5_event_count','事件'),
        'C7_selected_bytes':('skill_directory_bytes + skill_first_bytes','字节'),
        'C7_all_bytes':('skill_directory_bytes + skill_first_bytes + skill_second_bytes + skill_third_bytes','字节'),
        'C7_saved_bytes':('skill_second_bytes + skill_third_bytes','字节'),
        'C9_total_ms':('retry_first_ms + retry_backoff_ms + retry_second_ms','ms'),
        'C9_attempts_ms':('retry_first_ms + retry_second_ms','ms'),
        'C9_backoff_ms':('retry_backoff_ms','ms'),
        'C9_attempt_count':('retry_attempt_count','attempt'),
        'C11_requests':('C11_requested','请求'),
        'C11_executions':('C11_executed','执行'),
        'C11_successes':('C11_succeeded','成功结果'),
        'C11_rejections':('C11_rejected','拒绝'),
        'C13_parallel_total_ms':('spawn_ms + parallel_children_ms + join_ms','ms'),
        'C13_saved_ms':('single_agent_ms - (spawn_ms + parallel_children_ms + join_ms)','ms'),
        'C14_first_expected_seq':('snapshot_cursor + 1','序号'),
        'C14_after_normal_expected_seq':('first_normal_seq + 1','序号'),
        'C14_missing_sequences':('gap_candidate_seq - (first_normal_seq + 1)','事件'),
        'C15_ui_ms':('launch_waiting_ui_ms - launch_start_ms','ms'),
        'C15_ready_ms':('client_ready_ms - launch_start_ms','ms'),
        'C15_wait_ms':('client_ready_ms - launch_waiting_ui_ms','ms'),
    }
    results={}
    for name,(expression,unit) in requests.items():
        value=calculate(expression,variables)
        results[name]={'expression':expression,'value':str(value),'rounded_integer':str(value.quantize(Decimal('1'),rounding=ROUND_HALF_UP)),'unit':unit}
    return {'tool':'calculations','implementation':'local Python CLI; Decimal, precision=40','input_kind':dataset['kind'],
            'numeric_example_chapters':[3,4,5,6,7,8,9,11,13,14,15,17],
            'variables':{k:str(v) for k,v in variables.items()},'results':results}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,default=ROOT/'examples/metrics-input.json');parser.add_argument('--output',type=Path,default=ROOT/'examples/calculation-results.json');args=parser.parse_args()
    raw=args.input.read_bytes();output=report(json.loads(raw));output['input_sha256']=hashlib.sha256(raw).hexdigest()
    experiments=ROOT/'examples/source-experiment-results.json'
    if experiments.exists():
        evidence=experiments.read_bytes();observations=json.loads(evidence)
        output['source_experiments']={'cases_checked':len(observations['cases']),'input_sha256':hashlib.sha256(evidence).hexdigest(),'case_ids':[row['id'] for row in observations['cases']]}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tool':'calculations','results':{k:v['value'] for k,v in output['results'].items()}},ensure_ascii=False))

if __name__=='__main__':main()
