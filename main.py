from taipy.gui import Gui, notify
import pandas as pd 
import taipy.gui.builder as tgb


data = pd.read_excel(
    io = "supermarket_sales.xlsx",
    engine="openpyxl",
    sheet_name="Sales",
    skiprows=3,
    usecols="B:R",
    nrows=1000,
)

data["hour"] = pd.to_datetime( data["Time"], format="%H:%M:%S").dt.hour

# print(data["hour"].head)

# Filter creations
cities = list(data["City"].unique())
customer_types = list(data["Customer_type"].unique())
gender = list(data["Gender"].unique())


layout = {
    "xaxis":{"title": ""},
    "yaxis":{"title": ""},
    "margin":{"1": 150},
}

def on_filter(state):
    if(
        len(state.cities) == 0
        or len(state.customer_types) == 0
        or len(state.gender) == 0
    ):
        notify(state, "Error!!", "No results found. Check the filters.")
        return
    
    state.data_filtered, state.sales_by_product_line, state.sales_by_hour = filter(
        state.cities, state.customer_types, state.gender
    )

def filter(cities, customer_types, gender):
    # Filter data based on user selection
    data_filtered = data[
        data["City"].isin(cities)
        & data["Customer_type"].isin(customer_types)
        & data["Gender"].isin(gender)
    ]

    # calculate sales by product line
    # print(data_filtered[["Product Line", "Total"]].head())

    sales_by_product_line = (
        data_filtered[["Product line", "Total"]]
        .groupby( by = "Product line").sum()
        .sort_values(by="Total", ascending=True)
        .reset_index()
    )

    sales_by_hour = (
        data_filtered[["hour", "Total"]]
        .groupby( by = "hour").sum()
        .sort_values(by="Total", ascending=True)
        .reset_index()
    )
    
    return data_filtered, sales_by_product_line, sales_by_hour

def to_text(value):
    return "{:,}".format(int(value))

with tgb.Page() as page:
    tgb.toggle(theme=True)
    tgb.text("📊 Sales Dashboard 📊", class_name="h1 text-center pb2")

    with tgb.layout("1 1 1", class_name="p1"):
        with tgb.part(class_name="card"):
            tgb.text('## Total Sales: ', mode="md")
            tgb.text("US ${to_text(data_filtered['Total'].sum())}", class_name="h4")

        with tgb.part(class_name="card"):
            tgb.text('## Average Sales: ', mode="md")
            tgb.text("US ${to_text(data_filtered['Total'].mean())}", class_name="h4")

        with tgb.part(class_name="card"):
            tgb.text('## Average Rating: ', mode="md")
            tgb.text(
                     "{round(data_filtered['Rating'].mean(), 1)}"
                     + "{'⭐' * int(round( data_filtered['Rating'].mean() ))}"
                     , class_name="h4")
            
    with tgb.layout("1 1 1", class_name="p1"):
        tgb.selector(
            value="{cities}",
            lov=cities,
            dropdown=True,
            multiple=True,
            label="Select cities",
            class_name="fullwidth",
            on_change=on_filter,
        )
        tgb.selector(
            value="{customer_types}",
            lov=customer_types,
            dropdown=True,
            multiple=True,
            label="Select customer types",
            class_name="fullwidth",
            on_change=on_filter,
        )
        tgb.selector(
            value="{gender}",
            lov=gender,
            dropdown=True,
            multiple=True,
            label="Select genders",
            class_name="fullwidth",
            on_change=on_filter,
        )

    with tgb.layout("1 1"):
        tgb.chart(
            "{sales_by_hour}",
            x="hour",
            y="Total",
            type="bar",
            title="Sales by Hour",
            layout=layout,
        )
        tgb.chart(
            "{sales_by_product_line}",
            x="Total",
            y="Product line",
            type="bar",
            orientation="h",
            layout=layout,
            title="Sales by Product Line",
        )
            
if __name__== "__main__":
    data_filtered, sales_by_product_line, sales_by_hour = filter(
        cities, customer_types, gender
    )
    Gui(page).run(
        title="Sales Dashboard Using Taipy",
        use_reloader=True,
        debug=True,
        watermark="",
        margin="4em",
        favicon="images/favicon-32x32.png"
    )