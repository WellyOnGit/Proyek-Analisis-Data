import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('./dashboard/main_data.csv')
    date_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col])
    df['shipping_time'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.total_seconds() / 86400
    df['approval_time'] = (df['order_approved_at'] - df['order_purchase_timestamp']).dt.total_seconds() / 3600
    df['total_delivery_time'] = (df['order_delivered_carrier_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
    df = df[df['total_delivery_time'] >= 0]
    return df

df = load_data()

st.title('E-commerce Business Insights Dashboard')

st.markdown("""1. Apa top product kategori?
> Kategori produk teratas berdasarkan jumlah pesanan adalah "bed bath table" dengan 11.629 pesanan, diikuti oleh "health beauty" dengan 9.745 pesanan, dan "sports_leisure" dengan 8.717 pesanan.

2. Negara apa yang memiliki penjualan terbanyak agar kita bisa mencari tahu dimana tempat yang cocok untuk kita melebihi anggaran iklan
> Mengenai penjualan terbanyak, negara bagian dengan penjualan tertinggi adalah Sao Paulo (SP) dengan total penjualan sebesar 5.300.857,70 , diikuti oleh Rio de Janeiro (RJ) dan Minas Gerais (MG). Jika kita ingin mengoptimalkan anggaran iklan, fokus pada daerah-daerah ini mungkin bisa memberikan hasil yang baik.


3. Negara apa yang memiliki pengiriman waktu tersingkat
> Meskipun ada perbedaan, waktu pengiriman di seluruh negara bagian yang diamati cukup konsisten, berkisar antara 2,95 hingga 3,33 hari.""")

st.header('1. Top Product Categories')
top_categories = df['product_category_name'].value_counts().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x=top_categories.index, y=top_categories.values, ax=ax)
ax.set_title('Top 10 Product Categories')
ax.set_xlabel('Product Category')
ax.set_ylabel('Count')

st.pyplot(fig)

st.header('2. Product Category Performance')
category_performance = df.groupby('product_category_name').agg({
    'price': 'sum',
    'order_id': 'count'
}).sort_values('price', ascending=False).head(10)
category_performance.columns = ['Total Sales', 'Number of Orders']
st.dataframe(category_performance)

st.header('3. Average Shipping Time by State')
# Calculate the average shipping time by state
avg_shipping_time = df.groupby('customer_state')['shipping_time'].mean().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=avg_shipping_time.index, y=avg_shipping_time.values, ax=ax)
ax.set_title('Top 10 States by Average Shipping Time')
ax.set_xlabel('Customer State')
ax.set_ylabel('Average Shipping Time (Days)')

st.pyplot(fig)

st.header('4. Top States by Sales Volume')
state_sales = df.groupby('customer_state')['price'].sum().sort_values(ascending=False).head()

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(x=state_sales.index, y=state_sales.values, ax=ax)

ax.set_title('Total Sales by State')
ax.set_xlabel('State')
ax.set_ylabel('Total Sales ($)')
st.pyplot(fig)

st.header('5. Approval Time vs Total Delivery Time')
fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(data=df, x='approval_time', y='total_delivery_time', hue='shipping_time', palette='viridis', size='shipping_time', ax=ax)
ax.set_title('Approval Time vs Total Delivery Time')
ax.set_xlabel('Approval Time (hours)')
ax.set_ylabel('Total Delivery Time (days)')
st.pyplot(fig)

st.header('6. Customer and Seller Analysis')
customer_performance = df.groupby('customer_unique_id').price.sum().reset_index()


seller_performance = df.groupby('seller_id').agg({
    'price': 'sum',
    'order_id': 'count'
}).sort_values('price', ascending=False).head(10)
seller_performance.columns = ['Total Sales', 'Number of Orders']

col1, col2 = st.columns(2)

# Display customer performance in the first column
with col1:
    st.header("Top 10 Customers by Sales")
    st.dataframe(customer_performance.sort_values(by='price',ascending=False).head(10))

# Display seller performance in the second column
with col2:
    st.header("Top 10 Sellers by Sales")
    st.dataframe(seller_performance)
