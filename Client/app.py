from flask import Flask, request, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/plot', methods=['POST'])
def plot_csv():
    # Extracting file and form data
    csv_file = request.files['csvFile']
    # title = request.form.get('txttitle')
    x_axis = request.form.get('x_lbl')  # Assuming this is your time series index
    y_axis = request.form.get('y_lbl')  # Assuming this is your time series values

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Convert 'DATE' to datetime format and set as index
    if x_axis == 'DATE':
        df[x_axis] = pd.to_datetime(df[x_axis])
        df.set_index(x_axis, inplace=True)

    # Plotting the historical Total kWh data
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df[y_axis], color='tab:blue', label='Historical ' + y_axis)
    plt.title('Historical ' + y_axis + ' Data')
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.legend()
    plt.grid(True)

    # Saving plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    hist_png = buffer.getvalue()
    buffer.close()

    # Encoding plot image to base64 to embed in HTML
    plot_hist = base64.b64encode(hist_png).decode('utf8')

    # Forecasting

    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from sklearn.model_selection import train_test_split

    train_data, test_data = train_test_split(df, test_size=12, shuffle=False)

    model = SARIMAX(train_data[y_axis], 
                order=(1, 1, 1),              # (p, d, q)
                seasonal_order=(1, 1, 1, 12)) # (P, D, Q, m)

    model_fit = model.fit(disp=False)

    forecast = model_fit.forecast(steps=12)

    # Fitting a SARIMA model for 'Bill Amount'
    bill_model = SARIMAX(train_data['Bill Amount'], 
                        order=(1, 1, 1),              # (p, d, q)
                        seasonal_order=(1, 1, 1, 12)) # (P, D, Q, m)

    # Fitting the model
    bill_model_fit = bill_model.fit(disp=False)

    # Forecasting the next 12 months for Bill Amount
    bill_forecast = bill_model_fit.forecast(steps=12)

    bill_forecast

    # Creating a new DataFrame to hold both historical and forecasted data
    combined_data = pd.concat([df[['Total kWh', 'Bill Amount']], pd.DataFrame({'Total kWh': forecast.values, 'Bill Amount': bill_forecast.values}, index=pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=12, freq='M'))])

    # Plotting the combined historical and forecasted data for Total kWh
    plt.figure(figsize=(10, 5))
    plt.plot(combined_data.index, combined_data[y_axis], color='tab:blue', label=y_axis)
    plt.scatter(combined_data.index[-12:], combined_data[y_axis][-12:], color='tab:orange', label='Forecasted ' + y_axis, zorder=5)
    plt.title('Historical and Forecasted ' + y_axis)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.legend()
    plt.grid(True)

    # Saving plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoding plot image to base64 to embed in HTML
    plot_url = base64.b64encode(image_png).decode('utf8')

    # Return img tag with plot
    return f'<img src="data:image/png;base64,{plot_hist}" alt="Plot Image">' f'<img src="data:image/png;base64,{plot_url}" alt="Plot Image">'

if __name__ == '__main__':
    app.run(debug=True)
