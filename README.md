# Firstrade Account History csv -> compare with sp500

A Streamlit-based dashboard to **compare your personal brokerage performance** against the S&P 500.
We have a streamlit web version or a ipynb version.
![image](https://github.com/user-attachments/assets/b76040ca-365a-4149-8ecf-feaa03b3d73c)


---

## 📖 Why this tool exists

Most retail investors dollar-cost average into individual stocks or ETFs and wonder:

- **“Am I beating the market?”**  
- **“Did my timing or stock picks really outperform simply buying the S&P 500?”**

This app gives you an **apples-to-apples** comparison by:

1. **Computing your money-weighted return (XIRR)** on all your cash flows and final portfolio value  
2. **Computing the S&P 500’s XIRR** if you had invested the same amounts on each of those dates  
3. **Comparing simple lump-sum CAGRs** for both your portfolio and a single S&P 500 purchase at your first trade date

Use it to validate your decisions, learn from your timing, and see whether active stock-picking truly added value over “just buy the index.”

---

## 🚀 Getting started

1. **Clone or download** this repo  
2. **Activate your virtual environment** (optional but recommended)
   ```bash
   source venv/bin/activate
   ```
3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app**
   ```bash
   streamlit run firstrade_vs_sp500_app.py
   ```

---

## 🖥️ User interface walkthrough

### 1. Upload your trade history
![image](https://github.com/user-attachments/assets/e7a7b76b-d684-4702-8aed-296a429ac4c7)

* In the **sidebar**, click **“Upload a Firstrade export (.csv)”**
* Use the **Trade History → Export CSV** report from your Firstrade account

### 2. Enter your current position
![image](https://github.com/user-attachments/assets/7df432cf-506f-4403-94f9-b23c616dd386)

* **Valuation date**: Defaults to today, but you can choose any past date
* **Current total market value**: Your portfolio’s mark-to-market value on that date

### 3. View instant results
![image](https://github.com/user-attachments/assets/ada473c7-8599-4547-9474-2f6e4c8dae64)

Once you’ve uploaded your CSV and entered your portfolio value, you’ll see:

| Metric                              | Definition                                                                                      |
| ----------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Total cash invested**             | Sum of all negative cash-flows (buy orders)                                                     |
| **Portfolio XIRR**                  | Internal rate of return on your actual cash-flows + final value                                 |
| **S\&P 500 XIRR (same cash-flows)** | XIRR if you had bought the S\&P 500 index on each date you traded, instead of your stocks       |
| **Portfolio CAGR (lump-sum)**       | CAGR treating your entire invested capital as if it went in on the date of your first trade     |
| **S\&P 500 CAGR (lump-sum)**        | CAGR if you had invested that same total into the S\&P 500 on your first trade date and held it |

You can also expand the **“Show raw cash-flows”** panel to inspect each date and amount.

---

## 🔍 Key assumptions & disclaimers

1. **Only trades + one final mark-to-market**

   * We ignore dividends, interest, fees, corporate actions, and interim sell orders.
   * All that matters is your buys (negative cash-flows) and the single end-of-period valuation.
   * **Did not consider cash in your account.**

2. **Money-weighted vs. time-weighted returns**

   * **XIRR** is *dollar-weighted*: it reflects your personal timing of contributions.
   * **CAGR (lump-sum)** is *time-weighted*: shows market performance if money were invested all at once.
   * We compute both so you can see how much of your return came from timing vs. overall market movement.

3. **Price alignment**

   * Trades on non-trading days (weekends/holidays) are mapped to the **most recent prior** trading day’s closing price.

4. **Year-fraction approximation**

   * We divide by 365 days—tiny rounding errors may occur over very long periods.

5. **No portfolio rebalancing or fees**

   * This is a *performance analysis*, not a full tax or fee calculation.

---

## 📈 Next steps & enhancements

* **Support dividends & corporate actions** to refine XIRR accuracy
* **Handle intermediate sell orders** explicitly, rather than only netting final value
* **Add other benchmarks** (e.g., Nasdaq Composite, MSCI World)
* **Export charts & tables** as PNG/CSV for your own reports
* **Mobile-friendly layout** for on-the-go performance checks

Feel free to file an issue or submit a pull request with your ideas!

---

*Happy investing—and may your returns beat the index!*
