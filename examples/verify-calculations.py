"""验证计算口径与无效输入；并核对本书展示的舍入值。"""
from decimal import Decimal
import json
from pathlib import Path
from calculations import calculate, report

root=Path(__file__).resolve().parents[1]
source=json.loads((root/'examples/metrics-input.json').read_text(encoding='utf-8'))
result=report(source)
assert result['results']['A_pass_percent']['value']=='90.0'
assert result['results']['B_pass_percent']['value']=='80.0'
assert Decimal(result['results']['token_reduction_percent']['value'])==30
assert Decimal(result['results']['pass_drop_percentage_points']['value'])==10
assert Decimal(result['results']['relative_gain_B_to_A_percent']['value'])==Decimal('12.500')
assert result['results']['A_tokens_per_pass']['rounded_integer']=='2222'
assert result['results']['B_tokens_per_pass']['rounded_integer']=='1750'
assert Decimal(result['results']['C6_baseline_bytes']['value'])==4000
assert Decimal(result['results']['C6_augmented_bytes']['value'])==4600
assert Decimal(result['results']['C6_increase_percent']['value'])==15
assert Decimal(result['results']['C8_saved_bytes']['value'])==9000
assert Decimal(result['results']['C8_reduction_percent']['value'])==75
expected={
    'C8_future_saved_bytes':27000,'C3_turn_count':1,'C3_step_count':2,'C3_attempt_count':3,'C3_tool_call_count':1,
    'C4_last_line':70,'C4_remaining_lines':50,'C5_messages':4,'C5_calls':1,'C5_events':11,
    'C7_selected_bytes':2600,'C7_all_bytes':10600,'C7_saved_bytes':8000,
    'C9_total_ms':1400,'C9_attempts_ms':1100,'C9_backoff_ms':300,'C9_attempt_count':2,
    'C11_requests':4,'C11_executions':2,'C11_successes':1,'C11_rejections':2,
    'C13_parallel_total_ms':1150,'C13_saved_ms':50,
    'C14_first_expected_seq':41,'C14_after_normal_expected_seq':42,'C14_missing_sequences':1,
    'C15_ui_ms':200,'C15_ready_ms':1000,'C15_wait_ms':800,
}
for name,value in expected.items():assert Decimal(result['results'][name]['value'])==value,name
assert calculate('(7 + 5) / 3',{})==4
assert calculate('0.1 + 0.2',{})==Decimal('0.3')
try:calculate("__import__('os')",{})
except ValueError:pass
else:raise AssertionError('Expression calls must be rejected')
bad=json.loads(json.dumps(source));bad['samples']['B'][0]['id']='different-task'
try:report(bad)
except AssertionError:pass
else:raise AssertionError('Unpaired task sets must be rejected')
for formula in ['1 / 0','missing + 1']:
    try:calculate(formula,{})
    except (ArithmeticError,KeyError):pass
    else:raise AssertionError('Invalid formula should fail')
print('Calculation contracts and displayed values verified.')
