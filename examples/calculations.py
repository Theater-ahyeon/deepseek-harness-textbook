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
    requests={
        'A_pass_percent':('A_passed / A_tasks * 100','%'),
        'B_pass_percent':('B_passed / B_tasks * 100','%'),
        'token_reduction_percent':('(A_tokens - B_tokens) / A_tokens * 100','%'),
        'pass_drop_percentage_points':('(A_passed / A_tasks - B_passed / B_tasks) * 100','百分点'),
        'relative_gain_B_to_A_percent':('((A_passed / A_tasks) / (B_passed / B_tasks) - 1) * 100','%'),
        'A_tokens_per_pass':('A_tokens / A_passed','token / 通过任务'),
        'B_tokens_per_pass':('B_tokens / B_passed','token / 通过任务'),
    }
    results={}
    for name,(expression,unit) in requests.items():
        value=calculate(expression,variables)
        results[name]={'expression':expression,'value':str(value),'rounded_integer':str(value.quantize(Decimal('1'),rounding=ROUND_HALF_UP)),'unit':unit}
    return {'tool':'calculations','implementation':'local Python CLI; Decimal, precision=40','input_kind':dataset['kind'],
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
