import pandas as pd
import streamlit as st


def render_bar_chart(data: dict):
    if not data:
        st.warning("No data available.")
        return


    if "skills" in data:

        df = pd.DataFrame(data["skills"])

        if df.empty:
            st.warning("No data found.")
            return

        st.subheader("Top Skills")

        st.bar_chart(
            df.set_index("skill")
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        return

 
    if "items" in data:

        df = pd.DataFrame(data["items"])

        if df.empty:
            st.warning("No data found.")
            return

        x = df.columns[0]
        y = df.columns[1]

        st.bar_chart(
            df.set_index(x)
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        return

    st.info("No chart can be generated from this response.")


def render_table(data):

    if data is None:
        st.warning("No data available.")
        return


    if isinstance(data, list):

        df = pd.DataFrame(data)


    elif isinstance(data, dict):
        if all(isinstance(v, list) for v in data.values()):

            df = pd.DataFrame(data)

        else:

            df = pd.DataFrame([data])

    else:

        st.write(data)
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )