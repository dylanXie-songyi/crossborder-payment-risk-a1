import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data_path= '/Users/dylan/Desktop/跨境交易出海：反欺诈 /case Github/case A1：跨境支付链路监控/github发布版/dataset/payment_auth_data.csv'
out_dir="/Users/dylan/Desktop/跨境交易出海：反欺诈 /case Github/case A1：跨境支付链路监控/github发布版/dashboard"
os.makedirs(out_dir,exist_ok=True)

df=pd.read_csv(data_path)
df.columns=[c.strip() for c in df.columns]
df['created_at']=pd.to_datetime(df['created_at'],errors='coerce')
df['is_approved']=(df['auth_status']=='Approved').astype(int)
df['date']=df['created_at'].dt.date
df['hour']=df['created_at'].dt.floor('h')

print(df.shape)
print(df.columns.tolist())
print(f"overall auth rate: {df['is_approved'].mean():.2%}")

daily=(
    df.groupby('date',as_index=False)
    .agg(
        auth_rate=('is_approved','mean'),
        txn_cnt=('is_approved','size'))  
)

plt.figure(figsize=(10,4))
plt.plot(daily['date'],daily['auth_rate'])
plt.title("Daily Auth Rate Trend")
plt.xlabel("Date")
plt.ylabel("Auth Rate")
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "auth_rate_trend.png"), dpi=200)
plt.close()
daily.to_csv(os.path.join(out_dir,"daily_auth_rate.csv"),index=False)
#找异常
daily["z"] = (daily["auth_rate"] - daily["auth_rate"].mean()) / daily["auth_rate"].std(ddof=0)
anomaly_days = daily.sort_values("z").head(3)
print("\n==== Lowest 3 days by z-score ====")
print(anomaly_days[["date", "auth_rate", "txn_cnt", "z"]].to_string(index=False))

#拆解来源
# 国家维度
by_country = (
    df.groupby("country")["is_approved"]
    .agg(auth_rate="mean", txn_cnt="size")
    .reset_index()
    .sort_values(["auth_rate", "txn_cnt"], ascending=[True, False])
)
by_country.to_csv(os.path.join(out_dir, "auth_rate_by_country.csv"), index=False)

#PSP 维度
by_psp = (
    df.groupby("psp_name")["is_approved"]
    .agg(auth_rate="mean", txn_cnt="size")
    .reset_index()
    .sort_values(["auth_rate", "txn_cnt"], ascending=[True, False])
)
by_psp.to_csv(os.path.join(out_dir, "auth_rate_by_psp.csv"), index=False)

# 国家 × 支付方式热力图
pivot = df.pivot_table(
    index="country",
    columns="payment_method",
    values="is_approved",
    aggfunc="mean"
).fillna(np.nan)

plt.figure(figsize=(10, 5))
plt.imshow(pivot.values, aspect="auto")
plt.colorbar(label="Auth Rate")
plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
plt.yticks(range(len(pivot.index)), pivot.index)
plt.title("Auth Rate Heatmap: Country × Payment Method")
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "country_payment_heatmap.png"), dpi=200)
plt.close()

# 定位,拆解 异常日/异常时段
# 重点排查日
focus_day = str(anomaly_days.iloc[0]["date"])
print("\n==== Focus day (most abnormal) ====")
print("focus_day =", focus_day)
df_focus = df[df["date"].astype(str) == focus_day].copy()

# 当天国家
focus_country = (
    df_focus.groupby("country")["is_approved"]
            .agg(auth_rate="mean", txn_cnt="size")
            .reset_index()
            .sort_values(["auth_rate", "txn_cnt"], ascending=[True, False])
)

focus_country.to_csv(os.path.join(out_dir, "focus_day_auth_by_country.csv"), index=False)

# 当天 PSP 拆解
focus_psp = (
    df_focus.groupby("psp_name")["is_approved"]
            .agg(auth_rate="mean", txn_cnt="size")
            .reset_index()
            .sort_values(["auth_rate", "txn_cnt"], ascending=[True, False])
)

focus_psp.to_csv(os.path.join(out_dir, "focus_day_auth_by_psp.csv"), index=False)


# 小时级趋势
hourly_focus = (
    df_focus.groupby("hour")["is_approved"]
            .agg(auth_rate="mean", txn_cnt="size")
            .reset_index()
            .sort_values("hour")
)

plt.figure(figsize=(10, 4))
plt.plot(hourly_focus["hour"], hourly_focus["auth_rate"])
plt.title(f"Hourly Auth Rate Trend (focus day: {focus_day})")
plt.xlabel("Hour")
plt.ylabel("Auth Rate")
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "focus_day_hourly_auth_rate.png"), dpi=200)
plt.close()

hourly_focus.to_csv(os.path.join(out_dir, "focus_day_hourly_auth_rate.csv"), index=False)



# Decline 拆解
declined = df[df["auth_status"] == "Declined"].copy()
declined["decline_code"] = declined["decline_code"].fillna("UNKNOWN")

decline_dist = (
    declined["decline_code"]
    .value_counts()
    .reset_index()
)
decline_dist.columns = ["decline_code", "cnt"]
decline_dist.to_csv(os.path.join(out_dir, "top_decline_code.csv"), index=False)

plt.figure(figsize=(8, 4))
plt.bar(decline_dist["decline_code"].astype(str), decline_dist["cnt"])
plt.title("Decline Code Distribution (All Declined)")
plt.xlabel("Decline Code")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "decline_code_dist.png"), dpi=200)
plt.close()

# focus day 的 decline code
declined_focus = df_focus[df_focus["auth_status"] == "Declined"].copy()
declined_focus["decline_code"] = declined_focus["decline_code"].fillna("UNKNOWN")

decline_focus_dist = (
    declined_focus["decline_code"]
    .value_counts()
    .reset_index()
)
decline_focus_dist.columns = ["decline_code", "cnt"]
decline_focus_dist.to_csv(os.path.join(out_dir, "focus_day_decline_code.csv"), index=False)

worst_country = by_country.iloc[0]["country"]
best_country = by_country.iloc[-1]["country"]

print("\n==== Quick Summary (for risk_strategy.md) ====")
print(f"Overall Auth Rate: {df['is_approved'].mean():.2%}")
print(f"Worst Country: {worst_country} ({by_country.iloc[0]['auth_rate']:.2%})")
print(f"Best  Country: {best_country} ({by_country.iloc[-1]['auth_rate']:.2%})")
print(f"Most abnormal day: {focus_day}")







