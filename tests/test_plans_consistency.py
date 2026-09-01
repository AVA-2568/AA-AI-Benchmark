"""套餐数据一致性测试（verify_plans 离线层）。

config.json 的套餐是性价比榜的地基：算术不自洽、档位额度反降这类硬伤
必须让 CI 红灯，而不是等榜单出错再回溯。时效/页面可达性属 WARN 级，
不在这里断言（见 scripts/verify_plans.py 与 plan-audit workflow）。
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import verify_plans as vp  # noqa: E402


def _load():
    return vp.load_plans()


def test_plans_have_valid_fields():
    """必填字段齐全、discount 在 (0,1]。"""
    errs = [e for p in _load() for e in vp.check_fields(p)]
    assert errs == []


def test_plans_arithmetic_consistent():
    """discount 与 monthly/implied_value(或 credit_value) 自洽（>5% 为硬伤）。"""
    errs = [e for p in _load() for e in vp.check_arithmetic(p)[0]]
    assert errs == []


def test_plan_families_monotonic():
    """同产品线月费升档时额度（implied_value/credit_value/tokens）非降。"""
    errs = vp.check_family_monotonic(_load())
    assert errs == []


def test_offline_audit_has_no_fail():
    """端到端：离线审计 0 FAIL（逐项断言已拆在上面，此为防回归兜底）。"""
    import datetime
    result = vp.audit(_load(), max_age_days=10**6,  # 时效层不影响本断言
                      today=datetime.date(2026, 9, 1), online=False)
    fails = [e for e in result["entries"] if e["status"] == "fail"]
    assert fails == []
