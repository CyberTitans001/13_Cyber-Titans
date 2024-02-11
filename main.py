import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout='wide',page_title='StartUp Analysis')

df = pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

def load_overall_analysis():
    st.title('Overall Analysis')

    # total invested amount
    total = round(df['amount'].sum())
    # max amount infused in a startup
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    # avg ticket size
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    # total funded startups
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Total', str(total) + ' Cr')
    with col2:
        st.metric('Max', str(max_funding) + ' Cr')

    with col3:
        st.metric('Avg', str(round(avg_funding)) + ' Cr')

    with col4:
        st.metric('Funded Startups', num_startups)

    st.header('MoM graph')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig3, ax3 = plt.subplots()
    ax3.plot(temp_df['x_axis'], temp_df['amount'])

    st.pyplot(fig3)


def load_investor_details(investor):
    st.title(investor)
    # Filter out rows with 0 values in the 'amount' column
    investor_df = df[df['investors'].str.contains(investor) & (df['amount'] > 0)]

    # Load the recent 5 investments of the investor
    last5_df = investor_df.head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)
    with col1:
        # Biggest investments
        big_series = investor_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        if not big_series.empty:
            fig, ax = plt.subplots()
            ax.bar(big_series.index, big_series.values)
            st.pyplot(fig)
        else:
            st.write("No data available for biggest investments.")

    with col2:
        vertical_series = investor_df.groupby('vertical')['amount'].sum()
        st.subheader('Sectors invested in')
        if not vertical_series.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(vertical_series, labels=vertical_series.index, autopct="%0.01f%%")
            st.pyplot(fig1)
        else:
            st.write("No data available for sectors invested in.")

    investor_df['year'] = investor_df['date'].dt.year
    year_series = investor_df.groupby('year')['amount'].sum()
    st.subheader('YoY Investment')
    if not year_series.empty:
        fig2, ax2 = plt.subplots()
        ax2.plot(year_series.index, year_series.values)
        st.pyplot(fig2)
    else:
        st.write("No data available for YoY Investment.")

def load_startup_details(startup_name):
    st.title(startup_name)
    
    startup_df = df[df['startup'] == startup_name]
    
    st.subheader('Overview')
    st.write(f"Total funding received: {startup_df['amount'].sum()} Cr")
    st.write(f"Number of funding rounds: {startup_df.shape[0]}")
    st.write(f"Verticals: {', '.join(startup_df['vertical'].unique())}")
    st.write(f"Locations: {', '.join(startup_df['city'].unique())}")
    
    st.subheader('Funding Details')
    st.write(startup_df[['date', 'amount', 'round', 'investors']])
    
    st.subheader('Top Investors')
    top_investors = startup_df['investors'].str.split(',').explode().value_counts().head()
    st.write(top_investors)
    
    st.subheader('Most Recent Investments')
    st.write(startup_df[['date', 'amount', 'round', 'investors']].head())


# Modify the option selection block to include the load_startup_details function
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    selected_startup = st.sidebar.selectbox('Select StartUp', sorted(df['startup'].unique().tolist()), key='startup_select')
    btn1 = st.sidebar.button('Find StartUp Details', key='startup_button')
    if btn1:
        load_startup_details(selected_startup)

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].str.split(',').sum())), key='investor_select')
    btn2 = st.sidebar.button('Find Investor Details', key='investor_button')
    if btn2:
        load_investor_details(selected_investor)