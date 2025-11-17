

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
# from services import calculate_3ema

load_dotenv()

@tool(show_result=True, stop_after_tool_call=True)
def calculate_3ema(stock: str) -> str:
    """Get 3 EMA signals and strategy for a given stock using 5-minute candles."""

    # Download 5-min interval data for the past day
    df = yf.download(tickers=stock, period="1d", interval="5m", progress=False)
    df.index = df.index.tz_convert("Asia/Kolkata")
    print(df.index)

    if df.empty:
        return f"No data found for stock: {stock}"

    # Calculate EMAs
    df["EMA_3"] = df["Close"].ewm(span=3, adjust=False).mean()
    df["EMA_8"] = df["Close"].ewm(span=8, adjust=False).mean()
    df["EMA_21"] = df["Close"].ewm(span=21, adjust=False).mean()

    # Initialize signal columns
    df["BuyEntry"] = 0
    df["SellEntry"] = 0
    df["BuyExit"] = 0
    df["SellExit"] = 0

    position = None  # Track whether we're in a buy or sell position

    for i in range(1, len(df)):
        ema3 = df["EMA_3"].iloc[i]
        ema8 = df["EMA_8"].iloc[i]
        ema21 = df["EMA_21"].iloc[i]

        if position is None:
            if ema3 > ema8 > ema21:
                df.at[df.index[i], "BuyEntry"] = 1
                position = "buy"
            elif ema3 < ema8 < ema21:
                df.at[df.index[i], "SellEntry"] = 1
                position = "sell"

        elif position == "buy":
            if not (ema3 > ema8 > ema21):
                df.at[df.index[i], "BuyExit"] = 1
                position = None

        elif position == "sell":
            if not (ema3 < ema8 < ema21):
                df.at[df.index[i], "SellExit"] = 1
                position = None

    # Keep only relevant columns for output
    df_out = df[["Open", "High", "Low", "Close", "BuyEntry", "SellEntry", "BuyExit", "SellExit"]]

    # Optional: Format output as string table
    df_out.index.name = "Datetime"
    output = df_out.to_string()

    return f"Strategy result for {stock.upper()}:\n\n{output}"





# Base model
chat_model = OpenAIChat(id="gpt-4o", )

# Yahoo Finance tools for relevant agents
finance_tools = YFinanceTools(enable_all=True)

# Agent: Portfolio Manager
portfolio_agent = Agent(
    name="Portfolio Manager",
    role="You provide suggestions and optimization advice for building and managing investment portfolios.",
    tools=[calculate_3ema,finance_tools],
    model=chat_model,
    markdown=True
)

# Agent: Equity Trading
equity_agent = Agent(
    name="Equity Trader",
    role="You provide analysis and help with equity (stock) trades, entry/exit points, and price monitoring.",
    model=chat_model,
    tools=[finance_tools,calculate_3ema],
    markdown=True,
    show_tool_calls=True
)

# Agent: Options Trading
options_agent = Agent(
    name="Options Trader",
    role="You handle options trading strategies like calls, puts, spreads, and Greeks-based analysis.",
    model=chat_model,
    markdown=True
)

# Agent: User Account Manager
user_account_agent = Agent(
    name="User Account Manager",
    role="You assist users with account details, profile settings, and personal investment goals.",
    model=chat_model,
    markdown=True
)

# Agent: Risk Analyst
risk_agent = Agent(
    name="Risk Analyst",
    role="You assess investment risk, diversification, drawdowns, beta, volatility, and recommend risk mitigation strategies.",
    model=chat_model,
    markdown=True
)


finance_team = Team(
    name="Finance Strategy Team",
    mode="route",
    model=chat_model,
    members=[
        portfolio_agent,
        equity_agent,
        options_agent,
        user_account_agent,
        risk_agent,
    ],
    description="Routes financial queries to specialized agents for portfolio, trading, and risk tasks.",
    instructions=[
        "Route the user's message to the most appropriate agent:",
        "- Portfolio questions → Portfolio Manager",
        "- Stock/equity trades → Equity Trader",
        "- Options trades → Options Trader",
        "- Account or profile queries → User Account Manager",
        "- Risk-related assessments → Risk Analyst",
        "If you're unsure, ask the user to clarify their request."
    ],
    show_members_responses=True,
    show_tool_calls=True,
    markdown=True
)


