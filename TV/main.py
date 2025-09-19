from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import time

# ---- Define State ----
class SetupState(TypedDict):
    steps: List[dict]
    current_step: int
    approved: bool
    result: str

# ---- TV Controller Mock Tool ----
class TVController:
    def send_command(self, cmd: str):
        print(f"[TV] Sending command: {cmd}")

    def send_text(self, text: str):
        print(f"[TV] Typing text: {text}")

tv = TVController()

# ---- Reset + Setup Sequence ----
FACTORY_RESET_SEQUENCE = ["POWER_ON", "MENU", "DOWN", "DOWN", "OK", "OK"]

SETUP_SEQUENCE = [
    {"step": "Select language", "action": ["DOWN", "OK"]},
    {"step": "Select country", "action": ["DOWN", "DOWN", "OK"]},
    {"step": "Accept terms", "action": ["RIGHT", "OK"]},
    {"step": "Connect WiFi", "action": ["TEXT:MyHomeWiFi", "TEXT:MyPassword", "OK"]},
    {"step": "Finalize", "action": ["OK"]},
]

# ---- Nodes ----
def intent_node(state: SetupState):
    print("👉 Detected intent: Factory Reset + Setup Wizard")
    state["steps"] = SETUP_SEQUENCE
    state["current_step"] = 0
    return state

def confirm_node(state: SetupState):
    confirm = input("⚠️ This will factory reset and erase all TV settings. Proceed? (yes/no): ")
    state["approved"] = confirm.lower().startswith("y")
    return state if state["approved"] else END

def factory_reset_node(state: SetupState):
    print("▶️ Performing factory reset...")
    for cmd in FACTORY_RESET_SEQUENCE:
        tv.send_command(cmd)
    print("⏳ Waiting for TV reboot (approx 120 sec)...")
    time.sleep(5)  # simulate wait (use 120s in real case)
    return state

def setup_step_node(state: SetupState):
    if state["current_step"] < len(state["steps"]):
        step = state["steps"][state["current_step"]]
        print(f"▶️ Step {state['current_step']+1}: {step['step']}")
        for act in step["action"]:
            if act.startswith("TEXT:"):
                tv.send_text(act.replace("TEXT:", ""))
            else:
                tv.send_command(act)
        state["current_step"] += 1
        return state
    else:
        state["result"] = "✅ TV factory reset + setup completed successfully."
        return END

# ---- Build Graph ----
graph = StateGraph(SetupState)
graph.add_node("intent", intent_node)
graph.add_node("confirm", confirm_node)
graph.add_node("factory_reset", factory_reset_node)
graph.add_node("setup_step", setup_step_node)

graph.set_entry_point("intent")
graph.add_edge("intent", "confirm")
graph.add_edge("confirm", "factory_reset")
graph.add_edge("factory_reset", "setup_step")
graph.add_edge("setup_step", "setup_step")  # loop until done
graph.add_edge("setup_step", END)

# ---- Compile ----
app = graph.compile()

# ---- Run Agent ----
final_state = app.invoke({})
print(final_state.get("result", "⚠️ Operation aborted."))
