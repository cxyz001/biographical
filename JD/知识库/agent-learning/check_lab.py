"""控制器检查，不用于证明真实模型质量。"""
from agent_lab import run, execute_tool

ok = run('查询订单 A1001')
assert ok['status'] == 'completed'
assert ok['trace'][0]['observation']['status'] == '已发货'
assert 'error' in execute_tool('lookup_order', {'order_id': 'A1002'}, 'u1')
assert run('查询我的订单')['trace'] == []
assert execute_tool('search_policy', {'query': '退货规则'}, 'u1')['hits'][0]['id'] == 'return-1'

def endless(messages, timeout):
    return {'action': 'tool', 'name': 'lookup_order', 'arguments': {'order_id': 'A1001'}}

assert run('重复查询', endless, max_steps=3)['status'] == 'step_limit'
assert run('坏输出', lambda m, t: [])['status'] == 'model_error'
assert run('超时', max_seconds=0)['status'] == 'timeout'
for name, arguments in [('delete_order', {}), ('lookup_order', {'order_id': 1}),
                        ('lookup_order', {'order_id': 'A1001', 'user_id': 'u2'})]:
    try:
        execute_tool(name, arguments, 'u1')
    except ValueError:
        pass
    else:
        raise AssertionError('非法调用未被拦截')
print('PASS: 查询、权限、追问、检索、步数限制、坏输出、超时、非法工具参数。')
