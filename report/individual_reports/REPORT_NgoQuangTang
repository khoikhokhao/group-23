# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Ngô Quang Tăng
- **Student ID**: 2A202600478
- **Date**: 4/6/2026

---

## I. Technical Contribution (15 Points)

My main technical contribution in this lab was extending the tool layer in `src/tools.py` by adding two new functions:
- a simple helper function for testing tool invocation,
- and a simulated email-sending function for candidate outreach.

These additions help demonstrate how a ReAct Agent can move beyond information retrieval and perform a practical action step after extracting the necessary candidate information.

### Modules Implementated
- `src/tools.py`

### Code Highlight

```text
TC4: "Trần Thị B có số điện thoại public không?"

Expected ReAct flow:
1. Action: search_candidates
   Action Input: Trần Thị B
2. Observation: returns candidate ID U02
3. Action: get_profile_text
   Action Input: U02
4. Observation: phone number is not public
5. Final Answer: Trần Thị B (U02) does not have a public phone number.
```
#documentation
I designed and validated a test case that measures whether the ReAct Agent can correctly use tools to answer a privacy-sensitive candidate query. The purpose of this test case is to show that a direct chatbot may answer too early or hallucinate, while the ReAct Agent succeeds by following the correct retrieval sequence:
- search for the candidate,
- identify the correct profile ID,
- retrieve profile details,
- and answer only from the returned observation.

---

## II. Debugging Case Study (10 Points)

### Problem Description
A failure scenario I encountered during the lab was related to the email-sending flow. The agent was expected to send an email to a candidate, but at first it did not have a reliable way to do that. In some cases, it attempted to act before confirming whether the candidate profile actually contained a valid email address.

This created an issue in the reasoning chain:
- the agent could retrieve a candidate,
- but there was no clear action tool for sending an email,
- and there was also no validation step to ensure the extracted email was valid before attempting the action.

As a result, the workflow was incomplete and unreliable.

### Diagnosis
The root cause was not only the missing email action itself, but also the absence of a safeguard around the email input. A ReAct agent is only as reliable as the tools and action constraints it is given. If the prompt allows the model to take an action without validation, the agent may try to continue with missing or malformed data.

In this case, the problem came from two factors:
1. **Missing tool support**: there was no dedicated function for candidate email outreach.
2. **Weak action constraint**: the agent needed a clearer instruction that it must only send email after extracting a valid address from `get_profile_text`.

This was a good example of how agent failures are often not caused by the LLM alone, but by the combination of:
- prompt design,
- tool specification,
- and lack of validation in the action layer.

### Solution
I fixed the issue by adding the `send_email_to_candidate()` function and clarifying the `SYSTEM_PROMPT` so that the agent could understand when and how to call this tool correctly.

The new function includes a simple validation rule:
- if the email string does not contain `@`, the action fails with an explicit error observation.

That improvement gives the agent much better feedback. Instead of silently failing or performing an invalid action, the system now returns a meaningful observation such as:

```text
Lỗi: Hành động thất bại. Địa chỉ email không hợp lệ hoặc bị thiếu.
```

With this solution, the ReAct loop becomes more robust:
1. the agent first searches for the candidate,
2. then retrieves the candidate profile,
3. then extracts the email,
4. validates it through the tool,
5. and only sends the outreach message if the email is valid.

This debugging case showed me that adding a tool is not enough by itself. A useful production-style tool must also include basic validation and clear failure messages so the agent can recover intelligently.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning
The `Thought` block helps the agent behave much more logically than a direct chatbot. Instead of immediately guessing an answer or performing an action too early, the agent is encouraged to break the task into steps.

For example, in the email outreach scenario, the agent should not directly send an email as soon as the user asks. It should reason through the process:
- find the candidate,
- get the profile ID,
- retrieve the profile text,
- locate the email address,
- check whether it is valid,
- then call `send_email_to_candidate`.

This step-by-step reasoning is much more reliable than a chatbot-style response because the final action is based on evidence gathered during the loop.

### 2. Reliability
The agent can still perform worse than a chatbot in some situations. For example:
- when the task is just casual conversation,
- when the user asks a simple factual question that does not need tools,
- when the model produces the wrong action format,
- when the agent gets stuck in repeated tool-calling loops and hits `MAX_ITERATIONS`.

Compared to a chatbot, the ReAct agent is more powerful, but it is also more complex and more fragile. It requires tool definitions, clear prompts, action parsing, and observation handling. If any of these pieces are weak, the agent may underperform.

### 3. Observation
`Observation` is the key mechanism that grounds the agent in reality. It tells the model what actually happened after a tool call.

In my contribution, this is especially clear in the email tool:
- if the email is invalid, the observation explicitly says that the action failed,
- if the email is valid, the observation confirms that the email was successfully sent.

That feedback directly influences the next reasoning step. For example, when the agent receives an error observation about an invalid email, it should not continue pretending the task succeeded. Instead, it should go back and retrieve the correct profile data before trying again.

This is where ReAct is stronger than a standard chatbot: the model does not rely only on internal reasoning, but also on environmental feedback from tools.

---

## IV. Future Improvements (5 Points)

### Scalability
To scale this into a production-level AI agent system, I would move long-running tools into an asynchronous task queue such as Celery or RabbitMQ. Real actions like SMTP email sending, API calls, or web scraping can take several seconds, and running them synchronously inside the agent loop would slow down the entire system. An asynchronous design would make the architecture more scalable and responsive.

### Safety
For safety, I would add a **Human-in-the-loop (HITL)** mechanism for irreversible actions such as sending real emails to candidates. Instead of sending immediately, the agent should generate a draft and wait for approval from a recruiter or headhunter. I would also add a lightweight supervisor LLM to review the email content before sending, ensuring that it is professional, relevant, and free from hallucinated or sensitive information.

### Performance
If the number of tools grows large, putting every tool description directly into the `SYSTEM_PROMPT` will overload the context window and increase the chance of wrong tool selection. To improve performance, I would apply a retrieval-based tool selection approach. Tool descriptions could be stored in a Vector Database, and the system would retrieve only the most relevant tools for the current query. This would reduce prompt size, improve tool selection quality, and make the agent more efficient in a larger system.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
