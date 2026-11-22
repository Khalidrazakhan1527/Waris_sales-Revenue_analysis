# Power BI Desktop setup

1. Import `output/sales_clean.csv` with Get Data → Text/CSV. Name the query **Sales**. In Power Query, set Order Date to Date, Quantity to Whole Number, Sales, Profit and Discount to Decimal Number and identifiers and dimensions to Text. Verify the output row count against `statistical_results.json`.
2. Create the Date table below, mark it as a date table, and create a one-to-many relationship from Date[Date] to Sales[Order Date], with single-direction filtering from Date. Sort Month by Month Number, and sort Year Month by Date YearMonth Sort.
3. Add each measure separately and format money as USD, growth, margin, share and discount as percentages, and Orders as an integer.
4. Place the KPI cards on the overview page. Add a line chart with Date[Year Month] on the axis and Revenue and Profit as values. Add region and category comparison charts and a segment matrix with Revenue, Profit, Profit Margin and Segment Revenue Share. Use the other share measures on their corresponding matrices.
5. Add slicers for Date[Year], Region, State, Category, Sub-Category and Segment. On a detail page add a product matrix with Product ID, Product Name, Revenue and Profit. Add a seasonality chart with Month and Average Monthly Revenue. Add a discount band matrix with units, Order Lines, Units per Line and Profit Margin. Use the dashboard and the README to reconcile values before saving your native Power BI report.

## Date table

```dax
Date =
ADDCOLUMNS(
    CALENDAR(DATE(YEAR(MIN(Sales[Order Date])),1,1),
             DATE(YEAR(MAX(Sales[Order Date])),12,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date],"MMM"),
    "Month Number", MONTH([Date]),
    "Year Month", FORMAT([Date],"yyyy-MM"),
    "Date YearMonth Sort", YEAR([Date])*100+MONTH([Date])
)
```

## Measures

```dax
Revenue = SUM(Sales[Sales])
Profit = SUM(Sales[Profit])
Profit Margin = DIVIDE([Profit], [Revenue])
Orders = DISTINCTCOUNT(Sales[Order ID])
Average Order Value = DIVIDE([Revenue], [Orders])
Average Discount = AVERAGE(Sales[Discount])
Units = SUM(Sales[Quantity])
Order Lines = COUNTROWS(Sales)
Units per Line = DIVIDE([Units], [Order Lines])
Region Revenue Share = DIVIDE([Revenue], CALCULATE([Revenue], ALLSELECTED(Sales[Region])))
Category Revenue Share = DIVIDE([Revenue], CALCULATE([Revenue], ALLSELECTED(Sales[Category])))
Segment Revenue Share = DIVIDE([Revenue], CALCULATE([Revenue], ALLSELECTED(Sales[Segment])))
Average Monthly Revenue =
    AVERAGEX(VALUES('Date'[Date YearMonth Sort]), COALESCE([Revenue], 0))
Revenue Growth YoY =
VAR ComparisonYear = MAX('Date'[Year])
VAR CurrentRevenue =
    CALCULATE([Revenue], REMOVEFILTERS('Date'), 'Date'[Year] = ComparisonYear)
VAR PriorRevenue =
    CALCULATE([Revenue], REMOVEFILTERS('Date'), 'Date'[Year] = ComparisonYear - 1)
RETURN DIVIDE(COALESCE(CurrentRevenue, 0) - PriorRevenue, PriorRevenue)
```

## Discount band calculated column on Sales

```dax
Discount Band =
SWITCH(TRUE(),
    Sales[Discount] = 0, "0%",
    Sales[Discount] <= .1, ">0–10%",
    Sales[Discount] <= .2, ">10–20%",
    Sales[Discount] <= .4, ">20–40%",
    ">40%"
)
```
