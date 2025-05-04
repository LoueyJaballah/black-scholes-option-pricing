import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def convert_to_continuous_rate(r_nominal, compounding_type):
    n = {"annual": 1, "semiannual": 2, "quarterly": 4}.get(compounding_type.lower(), 1)
    return n * np.log(1 + r_nominal / n)

current_plot_params = {}

def calculate_and_plot():
    try:
        S = float(stock_price_var.get())
        K = float(strike_price_var.get())
        T = float(time_to_maturity_var.get())
        r_nominal = float(risk_free_rate_var.get())
        sigma = float(volatility_var.get())
        option_type = option_type_var.get().lower()
        compounding = compounding_var.get().lower()

        r = convert_to_continuous_rate(r_nominal, compounding)
        price = black_scholes(S, K, T, r, sigma, option_type)
        result_label.config(text=f"{option_type.capitalize()} option price at T={T:.2f} is: {price:.2f}")

        T_values = np.linspace(T, 0.001, 100)
        prices = [black_scholes(S, K, t, r, sigma, option_type) for t in T_values]

        current_plot_params.clear()
        current_plot_params.update({
            "T_values": T_values,
            "prices": prices,
            "option_type": option_type,
            "T": T
        })

        draw_plot()
    except Exception as e:
        messagebox.showerror("Input Error", f"Please check your inputs.\n{e}")

def draw_plot():
    for widget in graph_frame.winfo_children():
        widget.destroy()

    if not current_plot_params:
        return

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    T_values = current_plot_params["T_values"]
    prices = current_plot_params["prices"]
    option_type = current_plot_params["option_type"]

    ax.plot(T_values, prices, label=f"{option_type.capitalize()} Price", color="#2a9d8f", linewidth=2)
    ax.set_xlabel("Time to Maturity (Years)", fontsize=12)
    ax.set_ylabel("Option Price", fontsize=12)
    ax.set_title(f"{option_type.capitalize()} Option Price Decay", fontsize=14, weight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.invert_xaxis()
    ax.legend()

    fig.tight_layout(pad=2)

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, graph_frame)
    toolbar.update()
    toolbar.pack(fill=tk.X)

def focus_next(event, next_widget):
    next_widget.focus_set()

# --- Main Window Setup ---
root = tk.Tk()
root.title("Black-Scholes Option Pricing")
root.state('zoomed')  # Open maximized/fullscreen
root.geometry("900x650")  # Optional fallback size
root.minsize(800, 600)

style = ttk.Style(root)
style.theme_use('clam')  # Modern, clean theme

main_frame = ttk.Frame(root, padding=(15, 15))
main_frame.pack(fill=tk.BOTH, expand=True)

main_frame.columnconfigure(0, weight=0)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

input_frame = ttk.Frame(main_frame, padding=(10, 10), relief=tk.RIDGE)
input_frame.grid(row=0, column=0, sticky="ns", padx=(0, 15), pady=5)

stock_price_var = tk.StringVar(value="")
strike_price_var = tk.StringVar(value="")
time_to_maturity_var = tk.StringVar(value="")
risk_free_rate_var = tk.StringVar(value="")
volatility_var = tk.StringVar(value="")
option_type_var = tk.StringVar(value="Call")
compounding_var = tk.StringVar(value="Annual")

def create_labeled_entry(parent, label_text, variable, row):
    label = ttk.Label(parent, text=label_text, font=("Segoe UI", 11))
    label.grid(row=row, column=0, sticky="w", pady=6)
    entry = ttk.Entry(parent, textvariable=variable, font=("Segoe UI", 11), width=15)
    entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10,0))
    parent.columnconfigure(1, weight=1)
    return entry

# Add title label at the top of input_frame
title_label = ttk.Label(input_frame, text="Option Pricing", font=("Segoe UI", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="nsew")

# Shift all input rows by +1
stock_price_entry = create_labeled_entry(input_frame, "Stock Price (S):", stock_price_var, 1)
strike_price_entry = create_labeled_entry(input_frame, "Strike Price (K):", strike_price_var, 2)
time_to_maturity_entry = create_labeled_entry(input_frame, "Time to Maturity (Years):", time_to_maturity_var, 3)
risk_free_rate_entry = create_labeled_entry(input_frame, "Risk-Free Rate (e.g. 0.05):", risk_free_rate_var, 4)
volatility_entry = create_labeled_entry(input_frame, "Volatility (e.g. 0.2):", volatility_var, 5)

ttk.Label(input_frame, text="Option Type:", font=("Segoe UI", 11)).grid(row=6, column=0, sticky="w", pady=6)
option_type_cb = ttk.Combobox(input_frame, textvariable=option_type_var, values=["Call", "Put"], state="readonly", font=("Segoe UI", 11), width=13)
option_type_cb.grid(row=6, column=1, sticky="ew", pady=6, padx=(10,0))

ttk.Label(input_frame, text="Rf Compounding Frequency:", font=("Segoe UI", 11)).grid(row=7, column=0, sticky="w", pady=6)
compounding_cb = ttk.Combobox(input_frame, textvariable=compounding_var, values=["Annual", "Semiannual", "Quarterly"], state="readonly", font=("Segoe UI", 11), width=13)
compounding_cb.grid(row=7, column=1, sticky="ew", pady=6, padx=(10,0))

calc_button = ttk.Button(input_frame, text="Calculate Option Price", command=calculate_and_plot)
calc_button.grid(row=8, column=0, columnspan=2, pady=(15, 10), sticky="ew")

result_label = ttk.Label(input_frame, text="", font=("Segoe UI", 12, "bold"), foreground="#264653")
result_label.grid(row=9, column=0, columnspan=2, pady=(10, 0), sticky="w")

entries = [stock_price_entry, strike_price_entry, time_to_maturity_entry,
           risk_free_rate_entry, volatility_entry, option_type_cb, compounding_cb]

for i in range(len(entries)-1):
    entries[i].bind("<Return>", lambda e, nxt=entries[i+1]: focus_next(e, nxt))
compounding_cb.bind("<Return>", lambda e: calculate_and_plot())

graph_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
graph_frame.grid(row=0, column=1, sticky="nsew")
graph_frame.columnconfigure(0, weight=1)
graph_frame.rowconfigure(0, weight=1)

root.mainloop()
