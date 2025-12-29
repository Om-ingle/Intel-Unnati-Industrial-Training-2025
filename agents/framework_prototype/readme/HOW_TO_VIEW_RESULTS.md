# 📊 How to View Agent Results

## 🚀 Quickest Way

### Option 1: Simple Test (Recommended for first-time)
```bash
python SIMPLE_TEST.py
```
Shows basic results from 2 agents - perfect for quick testing!

---

### Option 2: View Full Results (Best for seeing everything)
```bash
# View all agents
python view_results.py

# View specific agent
python view_results.py research
python view_results.py qa
python view_results.py content
```

This shows **COMPLETE** results with all details!

---

### Option 3: Individual Test Scripts
```bash
# Research Agent
python test_research_agent.py

# Q&A Agent
python test_qa_agent.py

# All Agents Demo
python demo_all_agents.py
```

---

## 📋 What Each Script Shows

### `SIMPLE_TEST.py`
- ✅ Quick summary and insights from Research Agent
- ✅ Answer from Q&A Agent
- ⚡ Fastest way to see if agents work

### `view_results.py`
- ✅ **ALL results** from each step
- ✅ Complete state contents
- ✅ Formatted output
- 🎯 **Best for seeing full answers!**

### `test_research_agent.py`
- ✅ Summary, insights, analysis
- ✅ Final report
- ✅ All available state keys

### `test_qa_agent.py`
- ✅ Enhanced answer
- ✅ Follow-up questions
- ✅ Final response

### `demo_all_agents.py`
- ✅ All 3 agents in one run
- ✅ Formatted output
- ✅ Quick overview

---

## 🔍 Understanding the Output

### Research Agent Results:
- `summary` - Generated summary
- `insights` - Key insights
- `analysis` - Analysis of search results
- `final_report` - Complete report

### Q&A Agent Results:
- `enhanced_answer` - Full answer
- `followup_questions` - Suggested questions
- `final_response` - Complete response

### Content Creator Results:
- `outline` - Content outline
- `introduction` - Article intro
- `main_content` - Main body
- `conclusion` - Conclusion
- `final_article` - Complete article

---

## 💡 Pro Tips

1. **First time?** → Run `python SIMPLE_TEST.py`
2. **Want to see everything?** → Run `python view_results.py`
3. **Specific agent?** → Run `python view_results.py [research|qa|content]`
4. **Debugging?** → Check the "All Available Keys" output to see what's in state

---

## 🐛 If You Don't See Results

1. **Check execution status:**
   ```python
   print(execution.status)  # Should be "completed"
   ```

2. **Check what keys exist:**
   ```python
   print(list(execution.state.get_all().keys()))
   ```

3. **Get any key:**
   ```python
   result = execution.state.get("key_name")
   print(result)
   ```

4. **See everything:**
   ```python
   print(execution.state.get_all())
   ```

---

**Happy viewing! 🎉**

