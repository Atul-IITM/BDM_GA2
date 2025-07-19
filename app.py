from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return render_template('error.html', message="Something went wrong. Please upload right document.")
        file = request.files['file']
        if file.filename == '':
            return render_template('error.html', message="Something went wrong. Please upload right document.")

        xls = pd.ExcelFile(file, engine="openpyxl")

        sku_df = pd.read_excel(xls, xls.sheet_names[0])
        sales_df = pd.read_excel(xls, xls.sheet_names[1])
        stocks_df = pd.read_excel(xls, xls.sheet_names[2])

        stocks_df["Category"] = stocks_df["Category"].str.strip()
        stocks_df["SKU"] = stocks_df["SKU"].str.strip()

        sales_and_sku_df = pd.merge(sales_df, sku_df, on="SKU", how="left")
        sales_and_sku_df["Date"] = pd.to_datetime(sales_and_sku_df["Date"])
        sales_and_sku_df["Sales"] = sales_and_sku_df["Sales"].astype(int)
        sales_and_sku_df["Price"] = sales_and_sku_df["Price"].astype(float)
        sales_and_sku_df["Sale Value"] = sales_and_sku_df["Sales"] * sales_and_sku_df["Price"]
        sales_and_sku_df["Category"] = sales_and_sku_df["Category"].str.strip()
        
        # Q2
        Q2="For the entire month, what is the total sale value of the game “LTA Wise City”? (INTEGER)"
        sale_value_lta_wise_city = sales_and_sku_df[
            sales_and_sku_df["Product Name"] == "LTA Wise City"
        ]
        ans2 = (sale_value_lta_wise_city["Price"] * sale_value_lta_wise_city["Sales"]).sum()

        # Q3
        Q3="What fraction of total sale quantity (Volume) did “Books” category achieve in the first week? (Jan 1 to Jan 7, both days included) (FLOAT between 0 and 1) Hint: Construct a Volume Pareto Chart"
        books_sales_and_sku = sales_and_sku_df["Category"] == "Books"
        date_filter = (sales_and_sku_df["Date"] >= pd.Timestamp("2025-01-01")) & (sales_and_sku_df["Date"] <= pd.Timestamp("2025-01-07"))
        total_books_sales = sales_and_sku_df[books_sales_and_sku & date_filter]["Sales"].sum()
        total_sales = sales_and_sku_df[date_filter]["Sales"].sum()
        ans3 = total_books_sales / total_sales if total_sales != 0 else 0

        # Q4
        Q4="What is the maximum sale value by a single SKU in a day across all days? (Sale Value = Sale Qty * Price per Qty) (INTEGER)"
        sales_and_sku_df["Sale Value"] = sales_and_sku_df["Sales"] * sales_and_sku_df["Price"]
        date_and_sku_vise_data = sales_and_sku_df.groupby(["SKU", "Date"])["Sale Value"].sum()
        ans4 = date_and_sku_vise_data.max()

        # Q5
        Q5="What is the maximum revenue generating category across all days? (STRING)"
        date_and_category_vise_df = sales_and_sku_df.groupby(["Category", "Date"])["Sale Value"].sum()
        ans5= date_and_category_vise_df.idxmax()[0]

        # Q6+
        transactions_raw = pd.read_excel(xls, xls.sheet_names[3])

        cities = []
        dates = []
        current_city = ""
        for i in range(1, len(transactions_raw.columns)):
            col_name = transactions_raw.columns[i]
            if "Pune" in str(col_name) or col_name == "Pune":
                current_city = "Pune"
            elif "Aurangabad" in str(col_name) or col_name == "Aurangabad":
                current_city = "Aurangabad"
            elif "Nasik" in str(col_name) or col_name == "Nasik":
                current_city = "Nasik"
            date_val = transactions_raw.iloc[0, i]
            cities.append(current_city)
            dates.append(date_val)

        new_columns = ["SKU"]
        for i in range(len(cities)):
            new_columns.append(f"{cities[i]}_{dates[i]}")

        transactions_clean = transactions_raw.iloc[1:].copy()
        transactions_clean.columns = new_columns

        transactions_list = []
        for col in transactions_clean.columns[1:]:
            city, date = col.split("_", 1)
            temp_df = transactions_clean[["SKU", col]].copy()
            temp_df["City"] = city
            temp_df["Date"] = pd.to_datetime(date)
            temp_df["Units"] = temp_df[col]
            temp_df = temp_df[["SKU", "City", "Date", "Units"]]
            transactions_list.append(temp_df)

        transactions_df = pd.concat(transactions_list, ignore_index=True)
        transactions_df = transactions_df.dropna()
        transactions_df["SKU"] = transactions_df["SKU"].str.strip()
        transactions_with_category = pd.merge(
            sku_df, transactions_df, on="SKU", how="left")
        transactions_with_category["Category"] = transactions_with_category["Category"].str.strip()
        transactions_with_category["Date"] = pd.to_datetime(transactions_with_category["Date"])
        transactions_with_category["Units"] = transactions_with_category["Units"].astype(int)
        # transactions_with_category.to_csv("transactions_with_category.csv", index=False)

        Q6="What fraction of total sale value did Mumbai achieve? (across all categories and days) (FLOAT between 0 and 1)"
        total_sales = sales_and_sku_df["Sale Value"].sum()
        mumbai_sales = (sales_and_sku_df[sales_and_sku_df["City"] == "Mumbai"])["Sale Value"].sum()
        ans6 = mumbai_sales / total_sales if total_sales != 0 else 0

        Q7="What is the no. of units of household category SKUs are in stock at the end of 17th Jan 2025 in Nasik DC? (INTEGER)"
        household_stocks = stocks_df[stocks_df["Category"] == "Household"]
        opening_household_stocks = household_stocks["Nashik"].sum()
        household_stocks_transfers_df = transactions_with_category[
            (transactions_with_category["Category"] == "Household")
            & (transactions_with_category["City"] == "Nasik")
            & (transactions_with_category["Date"] <= pd.Timestamp("2025-01-15"))
        ]
        household_stocks_transfers = household_stocks_transfers_df["Units"].sum()
        total_household_sales = sales_and_sku_df[
            (sales_and_sku_df["Category"] == "Household")
            & (sales_and_sku_df["City"] == "Nasik")
            & (sales_and_sku_df["Date"] <= pd.Timestamp("2025-01-15"))
        ]["Sales"].sum()
        ans7 = opening_household_stocks + household_stocks_transfers - total_household_sales

        Q8="Based on the sales and stock data of Jan 2025, how many average days of inventory of SKU M003 are available in Pune? (FLOAT)"
        def average_days_inventory(sku, city):
            opening_stocks = stocks_df[(stocks_df["SKU"] == sku)][city].values[0]
            incomming_stocks = transactions_df[
                (transactions_df["SKU"] == sku) & (transactions_df["City"] == city)
            ]["Units"].sum()
            total_sales_monthly = sales_and_sku_df[
                (sales_and_sku_df["SKU"] == sku) & (sales_and_sku_df["City"] == city)
            ]["Sales"].sum()
            sales_average = total_sales_monthly / 31 if total_sales_monthly != 0 else 1
            closing_stocks = opening_stocks + incomming_stocks - total_sales_monthly
            average_stocks = (opening_stocks + closing_stocks) / 2
            return average_stocks / sales_average if sales_average != 0 else 0

        ans8 = average_days_inventory("M003", "Pune")

        Q9="Which SKU has the highest average days of inventory in Aurangabad? (STRING)"
        sku_list = stocks_df["SKU"].unique()
        max_days = 0
        max_sku = ""
        for sku in sku_list:
            days = average_days_inventory(sku, "Aurangabad")
            if days > max_days:
                max_days = days
                max_sku = sku
        ans9 = max_sku

        Q10="How many SKUs hold at least one weeks’ worth of inventory on average in Pune? (INTEGER)"
        sku_with_week_inventory = 0
        for sku in sku_list:
            days_inventory = average_days_inventory(sku, "Pune")
            if days_inventory >= 7:
                sku_with_week_inventory += 1
        ans10 = sku_with_week_inventory

        Q11="What is the closing stock of K005 at the end of the month in Nasik? (INTEGER)"
        opening_stocks_k005_nasik = stocks_df[
            (stocks_df["SKU"] == "K005")
        ]["Nashik"].values[0]
        incomming_stock_k005_nasik = transactions_df[
            (transactions_df["SKU"] == "K005")
            & (transactions_df["City"] == "Nasik")
        ]["Units"].sum()
        sales_k005_nasik = sales_and_sku_df[
            (sales_and_sku_df["SKU"] == "K005")
            & (sales_and_sku_df["City"] == "Nasik")
        ]["Sales"].sum()
        closing_stock_k005_nasik = opening_stocks_k005_nasik + incomming_stock_k005_nasik - sales_k005_nasik
        ans11 = closing_stock_k005_nasik

        
        
        return render_template('ans.html', 
                               ans2=ans2, ans3=ans3, ans4=ans4, ans5=ans5,
                               ans6=ans6, ans7=ans7, ans8=ans8, ans9=ans9,
                               ans10=ans10, ans11=ans11,Q2=Q2, Q3=Q3,
                               Q4=Q4, Q5=Q5, Q6=Q6, Q7=Q7,
                               Q8=Q8, Q9=Q9, Q10=Q10,
                               Q11=Q11)

    except Exception as e:
        # Optional: log e for debugging
        return render_template('error.html', message="Something went wrong. Please upload right document.")

if __name__ == '__main__':
    app.run(debug=True)
