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
