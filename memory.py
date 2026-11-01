MAX_TURNS = 4


def init_memory(st):
    if "memory" not in st.session_state:
        st.session_state.memory = {}


def get_memory(st, subject):
    return st.session_state.memory.get(subject, [])


def add_to_memory(st, subject, question, answer):
    history = st.session_state.memory.get(subject, [])
    history.append((question, answer))
    st.session_state.memory[subject] = history[-MAX_TURNS:]
