import streamlit as st
from main import run_agents

st.title('PM Dashboard (Multi-Agent System)')

context, blockers, actions = run_agents('PM Dashboard sample dataset.xlsx')

st.header('Project Summary')
st.write(context.get('summary', 'No summary available.'))

st.header('Blockers & Risks')
if blockers.get('blockers'):
    for b in blockers['blockers']:
        st.write(f"- {b}")
else:
    st.write('No blockers detected.')

st.header('Action Plan / Next Steps')
if actions.get('actions'):
    for a in actions['actions']:
        st.write(f"- {a}")
else:
    st.write('No actions recommended.') 