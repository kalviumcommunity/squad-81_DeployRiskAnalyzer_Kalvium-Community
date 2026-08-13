"""
Signup Funnel Analysis (Assignment Tasks)
Implements:
1. Defining funnel stages and counting users at each stage.
2. Computing drop-off rates between stages and identifying the biggest drop.
3. Visualizing the signup funnel using matplotlib.
4. Calculating the monetary business impact of each drop-off.
5. Providing actionable recommendations for optimizing the funnel.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def generate_funnel_df():
    """
    Generates a synthetic DataFrame of 10,000 rows matching the signup funnel stage counts:
    - 10,000 click signup
    - 8,000 enter email
    - 6,000 create password
    - 5,000 verify email
    - 4,000 add payment
    - 2,000 make first purchase
    """
    np.random.seed(42)
    n = 10000
    
    # We construct columns sequentially to represent funnel logic (users can only reach next stage if they completed the current one)
    signup_completed = np.ones(n, dtype=int)
    
    email_entered = np.zeros(n, dtype=int)
    email_entered[:8000] = 1
    
    password_created = np.zeros(n, dtype=int)
    password_created[:6000] = 1
    
    email_verified = np.zeros(n, dtype=int)
    email_verified[:5000] = 1
    
    payment_added = np.zeros(n, dtype=int)
    payment_added[:4000] = 1
    
    first_purchase = np.zeros(n, dtype=int)
    first_purchase[:2000] = 1
    
    df = pd.DataFrame({
        'user_id': np.arange(1, n + 1),
        'signup_completed': signup_completed,
        'email_entered': email_entered,
        'password_created': password_created,
        'email_verified': email_verified,
        'payment_added': payment_added,
        'first_purchase': first_purchase
    })
    
    # Shuffle the DataFrame rows to look realistic while retaining counts
    df = df.sample(frac=1).reset_index(drop=True)
    return df

def main():
    print("==================================================")
    print("         SIGNUP FUNNEL ANALYSIS PIPELINE         ")
    print("==================================================")

    # Task 1: Define Funnel Stages and Count Users
    print("\n--- Task 1: Define Funnel Stages and Count Users ---")
    df = generate_funnel_df()

    stage1_signup = len(df[df['signup_completed'] == 1])
    stage2_email = len(df[df['email_entered'] == 1])
    stage3_password = len(df[df['password_created'] == 1])
    stage4_verified = len(df[df['email_verified'] == 1])
    stage5_payment = len(df[df['payment_added'] == 1])
    stage6_purchase = len(df[df['first_purchase'] == 1])

    stages = {
        'Sign Up': stage1_signup,
        'Email Entered': stage2_email,
        'Password Created': stage3_password,
        'Email Verified': stage4_verified,
        'Payment Added': stage5_payment,
        'First Purchase': stage6_purchase
    }
    
    print("Funnel stage user counts:")
    for stage, count in stages.items():
        print(f"  {stage}: {count:,} users")

    # Task 2: Compute Drop-Off Rate Between Stages
    print("\n--- Task 2: Compute Drop-Off Rate Between Stages ---")
    stage_list = list(stages.values())
    stage_names = list(stages.keys())

    drop_off = []
    for i in range(len(stage_list) - 1):
        users_before = stage_list[i]
        users_after = stage_list[i+1]
        users_lost = users_before - users_after
        drop_pct = (users_lost / users_before) * 100
        
        drop_off.append({
            'from_stage': stage_names[i],
            'to_stage': stage_names[i+1],
            'users_before': users_before,
            'users_after': users_after,
            'users_lost': users_lost,
            'completion_rate': (users_after / users_before) * 100,
            'drop_rate': drop_pct
        })

    funnel_df = pd.DataFrame(drop_off)
    
    # Formatted version for display
    display_df = funnel_df.copy()
    display_df['completion_rate'] = display_df['completion_rate'].apply(lambda x: f"{x:.1f}%")
    display_df['drop_rate'] = display_df['drop_rate'].apply(lambda x: f"{x:.1f}%")
    print(display_df[['from_stage', 'to_stage', 'users_lost', 'completion_rate', 'drop_rate']])

    # Find biggest drop
    biggest_drop_idx = funnel_df['users_lost'].idxmax()
    biggest_drop_pct_idx = funnel_df['drop_rate'].idxmax()
    
    print(f"\nBiggest drop by absolute users lost: {funnel_df.loc[biggest_drop_idx]['from_stage']} -> {funnel_df.loc[biggest_drop_idx]['to_stage']} ({funnel_df.loc[biggest_drop_idx]['users_lost']:,} users)")
    print(f"Highest drop-off rate (%): {funnel_df.loc[biggest_drop_pct_idx]['from_stage']} -> {funnel_df.loc[biggest_drop_pct_idx]['to_stage']} ({funnel_df.loc[biggest_drop_pct_idx]['drop_rate']:.1f}%)")

    # Task 3: Visualize Funnel
    print("\n--- Task 3: Visualize Funnel ---")
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    ax.bar(stages.keys(), stages.values(), color=colors)

    ax.set_ylabel('Users', fontsize=12)
    ax.set_xlabel('Stage', fontsize=12)
    ax.set_title('Signup Funnel: Volume by Stage', fontsize=14)
    ax.set_ylim(0, max(stages.values()) * 1.15)

    # Annotate counts
    for stage, count in stages.items():
        ax.text(stage, count, f"{count:,}", ha='center', va='bottom', fontweight='bold')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('funnel_chart.png', dpi=150)
    plt.savefig('output/funnel_chart.png', dpi=150)
    plt.close()

    print("Funnel visualization saved to funnel_chart.png and output/funnel_chart.png")

    # Task 4: Calculate Business Impact of Each Drop-Off
    print("\n--- Task 4: Calculate Business Impact of Each Drop-Off ---")
    # Revenue value per customer completing the funnel
    revenue_per_customer = 100

    impact_analysis = []
    for idx, row in funnel_df.iterrows():
        users_lost = row['users_lost']
        revenue_lost = users_lost * revenue_per_customer
        impact_analysis.append({
            'drop_point': f"{row['from_stage']} -> {row['to_stage']}",
            'users_lost': users_lost,
            'revenue_impact': revenue_lost,
            'priority': 'HIGH' if revenue_lost > 150000 else 'MEDIUM'
        })

    impact_df = pd.DataFrame(impact_analysis)
    
    # Formatted version for display
    display_impact = impact_df.copy()
    display_impact['revenue_impact'] = display_impact['revenue_impact'].apply(lambda x: f"${x:,.0f}")
    print(display_impact.sort_values('users_lost', ascending=False))

    # Task 5: Actionable Recommendation
    print("\n--- Task 5: Actionable Recommendation ---")
    # Find highest priority bottleneck by absolute users/revenue lost
    highest_impact_row = funnel_df.loc[biggest_drop_idx]
    
    recommendation = f"""
FUNNEL OPTIMIZATION PRIORITY REPORT:
-----------------------------------
CRITICAL BOTTLENECK:
Stage: {highest_impact_row['from_stage']} -> {highest_impact_row['to_stage']}
Users Lost: {highest_impact_row['users_lost']:,.0f}
Drop Rate: {highest_impact_row['drop_rate']:.1f}%
Completion Rate: {highest_impact_row['completion_rate']:.1f}%
Revenue Impact (LTV/Purchases Lost): ${highest_impact_row['users_lost'] * revenue_per_customer:,.0f}

WHY DOES THE DROP-OFF OCCUR? (HYPOTHESES):
1. Payment Added -> First Purchase Drop-off (50.0% drop rate):
   - Friction at Checkout: Checkout flow might be too complex, or extra fees (taxes/shipping) are revealed too late.
   - Trust and Security: Users might hesitate to finalize the transaction if they lack trust in the checkout flow.
   - Payment Failures: Errors in payment gateway processing or lack of preferred local payment methods.
2. Sign Up -> Email Entered Drop-off (20.0% drop rate):
   - Signup form length is discouraging.
   - CTA is unclear or landing page value proposition is weak.

RECOMMENDED ACTION PLAN:
1. Conduct an A/B test simplifying the checkout page (e.g. one-click purchase, transparent pricing).
2. Implement exit-intent popups with a limited-time coupon or live-chat assistance.
3. Optimize payment failure handling (retry logic, alternative payment options like UPI, wallets).
4. Monitor drop-off rates continuously before and after optimization rollout.

EXPECTED BUSINESS IMPACT:
If we improve the {highest_impact_row['from_stage']} -> {highest_impact_row['to_stage']} completion rate by 10% (relative improvement):
- Additional conversions: {int(highest_impact_row['users_lost'] * 0.1):,.0f} users
- Additional revenue: ${int(highest_impact_row['users_lost'] * 0.1 * revenue_per_customer):,.0f}
"""
    print(recommendation)

    # Save summary report to output/funnel_analysis_report.txt
    with open('output/funnel_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(recommendation)
    print("Saved recommendation report to output/funnel_analysis_report.txt")

if __name__ == '__main__':
    main()
