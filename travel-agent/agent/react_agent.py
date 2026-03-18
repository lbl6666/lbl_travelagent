import re
from models.llm import chatmodel
from tools import get_weather
from tools import get_attraction
from react_prompt import AGENT_SYSTEM_PROMPT
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}



def run_agent(user_prompt: str, max_steps: int = 5):
    """
    Agent主执行函数

    Args:
        user_prompt: 用户输入
        max_steps: 最大推理轮数

    Returns:
        final_answer: 最终答案
    """
    print(f"用户输入: {user_prompt}\n" + "="*40)
    prompt_history = [f"用户请求: {user_prompt}"]

    for i in range(max_steps):
        print(f"--- 循环 {i+1} ---\n")
        # 1. 构建prompt
        full_prompt = "\n".join(prompt_history)

        # 2. 调用LLM
        llm_output = chatmodel.generate(
            full_prompt,
            system_prompt=AGENT_SYSTEM_PROMPT
        )

        # 3. 截断多余输出
        match = re.search(
            r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)',
            llm_output,
            re.DOTALL
        )
        if match:
            llm_output = match.group(1).strip()
        print(f"模型输出:\n{llm_output}\n")
        prompt_history.append(llm_output)

        # 4. 解析Action
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            prompt_history.append(
                "Observation: 错误: 未能解析到 Action 字段"
            )
            continue

        action_str = action_match.group(1).strip()

        # 5. 判断是否结束
        if action_str.startswith("Finish"):
            final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
            print(f"任务完成，最终答案: {final_answer}")
            return final_answer

        # 6. 解析工具调用
        tool_name = re.search(r"(\w+)\(", action_str).group(1)
        args_str = re.search(r"\((.*)\)", action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        # 7. 调用工具
        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误：未定义的工具 '{tool_name}'"

        # 8. 写回上下文
        print(f"{observation}\n" + "="*40)
        prompt_history.append(f"Observation: {observation}")

    return "任务未完成（达到最大推理步数）"