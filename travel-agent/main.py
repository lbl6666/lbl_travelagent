from agent.react_agent import run_agent

if __name__ == "__main__":
    query = "帮我查一下北京天气并推荐景点"
    result = run_agent(query)
    print("最终结果：", result)