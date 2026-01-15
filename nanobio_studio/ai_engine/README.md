# AI Engine Module - Complete Documentation Index

## 📚 Documentation Files

### Getting Started
1. **[QUICK_START.md](QUICK_START.md)** ⭐ **START HERE**
   - 5-minute setup
   - Common scenarios
   - Code examples
   - Troubleshooting
   - Streamlit integration

### Complete Reference
2. **[API_REFERENCE.md](API_REFERENCE.md)** 📖 Comprehensive Guide
   - Full module descriptions
   - Class & function signatures
   - Data types
   - Usage examples
   - Best practices
   - Performance metrics

### Architecture & Structure
3. **[MODULE_STRUCTURE.md](MODULE_STRUCTURE.md)** 🏗️ Architecture Guide
   - Module hierarchy
   - Module responsibilities
   - Design patterns
   - Data flow diagrams
   - Integration points
   - Performance characteristics

### Implementation Details
4. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** ✅ What Was Built
   - What was implemented
   - Files created/modified
   - Key features
   - Usage examples
   - Validation checklist

---

## 🔧 Module Quick Reference

### Entry Point
```python
from nanobio_studio.ai_engine import create_engine, get_scenarios

engine = create_engine(simulate_fn=my_simulator)
result = engine.run_scenario("safety_first", design_space)
```

### Core Modules

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| **engine.py** | Orchestrator | `AIEngine`, `create_engine()` |
| **optimizer.py** | Optimization | `run_optimization()` |
| **scenarios.py** | Presets | `get_scenarios()`, `ScenarioPreset` |
| **objectives.py** | Efficacy | `efficacy_proxy()` |
| **toxicity.py** | Toxicity | `toxicity_score_hybrid()` |
| **cost.py** | Cost | `cost_score_proxy()` |
| **uncertainty.py** | Confidence | `simple_confidence_from_rules()` |
| **explainability.py** | Analysis | `explain_design()` |
| **pareto.py** | Pareto | `pareto_front()`, `is_dominated()` |
| **audit.py** | Compliance | `AuditRecord`, `audit_to_html()` |
| **reporting.py** | Export | `candidates_to_df()` |
| **simulator_adapter.py** | Simulation | `SimulateFn` |
| **schema.py** | Types | `DesignSpace`, `ObjectiveWeights` |

---

## 🚀 Quick Start Checklist

- [ ] Read **QUICK_START.md** (5 min)
- [ ] Copy 5-minute setup code
- [ ] Install simulator function
- [ ] Run first optimization
- [ ] Export results
- [ ] Read **API_REFERENCE.md** for details

---

## 📖 Learning Path

### Level 1: Beginner (15 minutes)
1. Read QUICK_START.md
2. Run basic example:
   ```python
   engine = create_engine(simulate_fn)
   result = engine.run_scenario("academic", space)
   print(result.best)
   ```

### Level 2: Intermediate (30 minutes)
1. Read API_REFERENCE.md (overview)
2. Try different scenarios
3. Use custom weights
4. Export DataFrame

### Level 3: Advanced (1 hour)
1. Read full API_REFERENCE.md
2. Read MODULE_STRUCTURE.md
3. Implement sensitivity analysis
4. Generate audit reports
5. Integrate with database

### Level 4: Expert (ongoing)
1. Read IMPLEMENTATION_SUMMARY.md
2. Study design patterns
3. Contribute enhancements
4. Customize scoring functions

---

## 🎯 Common Tasks

### Task: Run optimization
→ See QUICK_START.md section "Run Optimization"

### Task: Choose a scenario
→ See QUICK_START.md section "Common Scenarios"

### Task: Understand results
→ See API_REFERENCE.md section "Usage Examples"

### Task: Export results
→ See QUICK_START.md section "Export Results"

### Task: Integrate with app
→ See QUICK_START.md section "Integration with Streamlit"

### Task: Troubleshoot issue
→ See QUICK_START.md section "Troubleshooting"

### Task: Understand architecture
→ See MODULE_STRUCTURE.md section "Data Flow"

### Task: Customize engine
→ See API_REFERENCE.md section "Configuration"

---

## 📊 6 Scenario Presets

| Scenario | Efficacy | Safety | Cost | Use Case |
|----------|----------|--------|------|----------|
| **academic** | 45% | 35% | 20% | Learning & exploration |
| **safety_first** | 30% | 55% | 15% | Translational/IND |
| **cost_constrained** | 35% | 30% | 35% | Manufacturing |
| **efficacy_driven** | 60% | 25% | 15% | Early research |
| **balanced** | 40% | 35% | 25% | General purpose |
| **regulatory_compliant** | 35% | 50% | 15% | FDA/EMA submission |

→ See QUICK_START.md for examples of each

---

## 🔗 Integration Guides

### With Streamlit
- See QUICK_START.md → "Integration with Streamlit"

### With Database
- Use `engine.get_audit_trail()` + `persistence.save_optimization_run()`

### With Your Simulator
- Pass `simulate_fn` to `create_engine()`
- Must return `SimulationResult`

→ See API_REFERENCE.md → "Simulation Integration"

---

## ✅ Feature Checklist

- ✅ Multi-objective optimization (Pareto)
- ✅ 6 pre-configured scenarios
- ✅ Custom objective weights
- ✅ Constraint enforcement
- ✅ Sensitivity analysis
- ✅ Pareto front extraction
- ✅ Confidence scoring
- ✅ Complete audit trail
- ✅ HTML report generation
- ✅ DataFrame export
- ✅ Logging & error handling
- ✅ Design space validation
- ✅ Reproducibility (seeding)

---

## 📝 Code Examples

### Minimal (3 lines)
```python
engine = create_engine(simulate_fn)
result = engine.run_scenario("academic", space)
print(result.best.efficacy)
```

### Basic (10 lines)
```python
engine = create_engine(simulate_fn)
result = engine.run_scenario("safety_first", space, n_trials=200)
pareto = engine.get_pareto_front(result)
df = engine.get_dataframe_report(result)
print(f"Best: {result.best.efficacy:.1f}")
print(f"Pareto: {len(pareto)} solutions")
df.to_csv("results.csv")
```

### Advanced (20 lines)
```python
engine = create_engine(simulate_fn, log_level="DEBUG")
result = engine.run_scenario("regulatory_compliant", space)
pareto = engine.get_pareto_front(result)
explanation = engine.explain_best(result, space)
audit_trail = engine.get_audit_trail()

print(f"Solutions: {len(result.candidates)}")
print(f"Drivers: {explanation['drivers']}")
df = engine.get_dataframe_report(result)
df.to_csv("designs.csv")

html = engine.get_html_report(audit_trail[0])
with open("report.html", "w") as f:
    f.write(html)
```

→ See QUICK_START.md for more examples

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | Check `nanobio_studio.ai_engine` path |
| No results | Check simulator, relax constraints |
| Slow | Use placeholder simulator, reduce trials |
| Memory error | Reduce trials, batch process |

→ See QUICK_START.md → "Troubleshooting" for details

---

## 📞 Support Resources

1. **Questions about usage?**
   → Read QUICK_START.md

2. **Need API details?**
   → Read API_REFERENCE.md

3. **Want to understand architecture?**
   → Read MODULE_STRUCTURE.md

4. **Curious about implementation?**
   → Read IMPLEMENTATION_SUMMARY.md

5. **Confused about something?**
   → Check the relevant module's docstrings

---

## 🔄 Version & Updates

| Version | Date | Status |
|---------|------|--------|
| 1.0 | Jan 15, 2026 | ✅ Complete |

---

## 📌 Key Takeaways

1. **Simple Interface**: `engine.run_scenario()` for quick starts
2. **Flexible**: Custom weights & constraints for advanced use
3. **Transparent**: Audit trail for regulatory compliance
4. **Extensible**: Pluggable simulators, adapters, patterns
5. **Well-Documented**: 1000+ lines across 4 files
6. **Production-Ready**: Error handling, logging, validation

---

## 🎓 Learning Resources

- **Pareto Optimization**: See MODULE_STRUCTURE.md
- **Multi-Objective**: See API_REFERENCE.md → "Multi-Objective Optimization"
- **Sensitivity Analysis**: See QUICK_START.md → "Sensitivity Analysis"
- **Uncertainty Quantification**: See API_REFERENCE.md → "uncertainty.py"
- **Design Patterns**: See MODULE_STRUCTURE.md → "Design Patterns"

---

**Happy optimizing! 🚀**

For questions or issues, see the appropriate documentation file above.

---

**Last Updated**: January 15, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready
