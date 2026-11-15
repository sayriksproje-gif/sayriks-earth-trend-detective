import pandas as pd
import numpy as np
from scipy import stats


def mann_kendall_test(values):
    """Basit Mann-Kendall trend testi (yaklaşık p-değeri, normal yaklaşım)."""
    x = np.asarray(values, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 8:
        return {"s": None, "z": None, "p_value": None, "trend": "Yetersiz veri", "significant": False}

    s = 0
    for i in range(n - 1):
        diff = x[i + 1:] - x[i]
        s += np.sum(np.sign(diff))

    # varyans (bağsız/ties az varsayımıyla)
    var_s = (n * (n - 1) * (2 * n + 5)) / 18.0
    if var_s <= 0:
        return {"s": int(s), "z": None, "p_value": None, "trend": "Belirsiz", "significant": False}

    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0

    p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
    if p_value < 0.05 and s > 0:
        trend = "Artan trend (anlamlı)"
        significant = True
    elif p_value < 0.05 and s < 0:
        trend = "Azalan trend (anlamlı)"
        significant = True
    elif s > 0:
        trend = "Artış eğilimi (anlamlı değil)"
        significant = False
    elif s < 0:
        trend = "Azalış eğilimi (anlamlı değil)"
        significant = False
    else:
        trend = "Belirgin trend yok"
        significant = False

    return {"s": int(s), "z": float(z), "p_value": p_value, "trend": trend, "significant": significant}


def calculate_trend_and_stats(df: pd.DataFrame):
    """
    Zaman serisi verileri üzerinden temel istatistik ve trend analizi hesaplar.
    Beklenen sütunlar: Date, Temperature (veya Value)
    """
    if df is None or df.empty:
        return None

    data = df.copy()
    # Yinelenen sütun adlarına karşı koruma
    if data.columns.duplicated().any():
        data = data.loc[:, ~data.columns.duplicated()].copy()

    temp_col = "Temperature" if "Temperature" in data.columns else ("Value" if "Value" in data.columns else None)
    if temp_col is None or "Date" not in data.columns:
        return None

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    temp_series = data[temp_col]
    if isinstance(temp_series, pd.DataFrame):
        temp_series = temp_series.iloc[:, 0]
    data["Temperature"] = pd.to_numeric(temp_series, errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["Date", "Temperature"])
    if data.empty:
        return None

    # NASA POWER bazı eksik değerleri -999 gibi döndürebilir; uç değerleri ayıkla
    data = data[data["Temperature"] > -100]
    if len(data) < 2:
        return None

    data = data.sort_values("Date")
    mean_val = float(data["Temperature"].mean())
    max_val = float(data["Temperature"].max())
    min_val = float(data["Temperature"].min())
    std_val = float(data["Temperature"].std(ddof=1)) if len(data) > 1 else 0.0

    data["Date_Ordinal"] = data["Date"].map(pd.Timestamp.toordinal)
    slope_per_day, intercept, r_value, p_value, std_err = stats.linregress(
        data["Date_Ordinal"], data["Temperature"]
    )
    slope_per_year = float(slope_per_day * 365.25)
    slope_per_decade = float(slope_per_year * 10)

    # %95 güven aralığı (eğim, yıllık ve 10 yıllık)
    try:
        dfree = max(int(len(data)) - 2, 1)
        tcrit = float(stats.t.ppf(0.975, dfree))
        ci_year = tcrit * float(std_err) * 365.25
        ci_decade = ci_year * 10
    except Exception:
        ci_year = None
        ci_decade = None

    n = int(len(data))
    if p_value < 0.05 and n >= 30:
        significance = "İstatistiksel olarak anlamlı (p < 0.05)"
    elif p_value < 0.05:
        significance = "Anlamlı eğilim sinyali var (p < 0.05), örneklem sınırlı"
    elif n < 30:
        significance = "Yetersiz/ sınırlı veri (örneklem küçük, p >= 0.05)"
    else:
        significance = "İstatistiksel olarak belirgin anlamlılık yok (p >= 0.05)"

    mk = mann_kendall_test(data["Temperature"].values)

    return {
        "count": n,
        "start_date": data["Date"].min(),
        "end_date": data["Date"].max(),
        "mean": mean_val,
        "max": max_val,
        "min": min_val,
        "std": std_val,
        "slope_per_day": float(slope_per_day),
        "slope_per_year": slope_per_year,
        "slope_per_decade": slope_per_decade,
        "slope_ci95_year": ci_year,
        "slope_ci95_decade": ci_decade,
        "intercept": float(intercept),
        "r_value": float(r_value),
        "r_squared": float(r_value ** 2),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "significance": significance,
        "mk_s": mk.get("s"),
        "mk_z": mk.get("z"),
        "mk_p_value": mk.get("p_value"),
        "mk_trend": mk.get("trend"),
        "mk_significant": mk.get("significant"),
    }