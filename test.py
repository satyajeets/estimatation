import pandas as pd
import numpy as np
import numpy_financial as npf

# Case shiller year over year % appriciation
CS_SF = 6.28
CS_SF_10 = 9.64
CS_US = 4.25
CS_US_10 = 6.52

# FHFA house price index yoy % appriciation
HPI_CALI = 6.92
HPI_USA = 4.89

def main():
    # vars
    down = 250000
    rate = 3.8
    principal = 1000000
    years = 30
    long_term_capital_gain_tax_rate = 0.15  # might change with income/laws

    # annual % costs
    yoy_appreciation = 0.07
    inflation = 0.07
    maintenance = 0.01
    property_tax = 0.01
    property_tax_increase = 0.02
    # property_tax_increase = 0.01
    home_insurance = 250 * 12
    hoa = 250 * 12

    # derived vars
    purchase_price = down + principal
    roi = rate / 100
    n = 12 * years  # no of payments
    i = roi / 12  # i%

    mortgage_amount = -(principal)
    interest_rate = (rate / 100) / 12
    periods = years * 12
    # CREATE ARRAY
    n_periods = np.arange(years * 12) + 1

    ##### BUILD AMORTIZATION SCHEDULE #####
    # INTEREST PAYMENT
    interest_monthly = npf.ipmt(interest_rate, n_periods, periods, mortgage_amount)

    # PRINCIPAL PAYMENT
    principal_monthly = npf.ppmt(interest_rate, n_periods, periods, mortgage_amount)

    # JOIN DATA
    df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
    df = pd.DataFrame(df_initialize, columns=['period', 'interest', 'principal'])

    # MONTHLY MORTGAGE PAYMENT
    df['monthly_payment'] = df['interest'] + df['principal']

    # CALCULATE CUMULATIVE SUM OF MORTAGE PAYMENTS
    # df['outstanding_balance'] = df['monthly_payment'].cumsum()
    df['outstanding_principal'] = principal - df['principal'].cumsum()

    # REVERSE VALUES SINCE WE ARE PAYING DOWN THE BALANCE
    # df.outstanding_balance = df.outstanding_balance.values[::-1]
    df = df.round(2)

    initial_property_tax = property_tax * purchase_price
    maintenance_cost = maintenance * purchase_price
    payment_no = 1
    apprecaited_property_price = purchase_price
    df['net_investment'] = down
    df['net_investment'][0] = down+df['monthly_payment'][0] + hoa/12 + home_insurance/12 + initial_property_tax/12 + maintenance_cost/12
    df['appreciated_price'] = apprecaited_property_price
    while payment_no < n:
        df['appreciated_price'][payment_no] = apprecaited_property_price
        # df['net_investment'][payment_no] = df['net_investment'][payment_no-1] + df['monthly_payment'][payment_no] + hoa/12 + home_insurance/12 + initial_property_tax/12 + maintenance_cost/12

        df['net_investment'][payment_no] = df['net_investment'][payment_no - 1] + df['monthly_payment'][
            payment_no] + hoa / 12 + home_insurance / 12 + initial_property_tax / 12

        if payment_no % 12 == 0:
            initial_property_tax = initial_property_tax + (initial_property_tax * property_tax_increase)
            maintenance_cost = maintenance_cost + maintenance_cost * inflation
            apprecaited_property_price = apprecaited_property_price + apprecaited_property_price*yoy_appreciation
        payment_no = payment_no + 1

    df['selling_agent_fee'] = 0.05 * df['appreciated_price']
    df['capital_gain'] = df['appreciated_price'] - purchase_price
    df['capital_gain_tax'] = 0
    # 500k is tax deductible for capital gain for married filing jointly as today
    df.loc[df['capital_gain'] < 500000, 'capital_gain_tax'] = 0
    df.loc[df['capital_gain'] > 500000, 'capital_gain_tax'] = (df['capital_gain'] - 500000) * long_term_capital_gain_tax_rate
    df['profit'] = df['appreciated_price'] - (df['outstanding_principal'] + df['net_investment'] + df['selling_agent_fee'] + df['capital_gain_tax'])
    # df['profit'] = df['appreciated_price'] - (df['outstanding_principal'] + df['net_investment'])

    x = [round(item) for item in df.period.values.tolist()]
    y = [round(item) for item in df.profit.values.tolist()]

    # format for readability. This changes fields to string from int/float
    for column in df:
        df[column] = df[column].apply(format)

    print(df.to_string(columns=['interest', 'principal', 'outstanding_principal', 'net_investment', 'appreciated_price', 'selling_agent_fee', 'capital_gain','capital_gain_tax', 'profit']))

def format(x):
    return "{0:,.2f}".format(x)

def yoy():
    down = 250000
    rent = 3500

if __name__ == "__main__":
    pd.set_option('mode.chained_assignment', None)
    main()
