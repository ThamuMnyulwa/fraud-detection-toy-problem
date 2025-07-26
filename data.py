import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def generate_coupon_abuse_dataset_with_user_info(
    n=150, abuse_rate=0.3, date_range_days=30
):
    random.seed(42)
    np.random.seed(42)

    # Base lists
    user_ids = [f"user_{i:03d}" for i in range(1, 101)]
    merchants = ["StoreA", "StoreB", "StoreC", "StoreD", "StoreE"]
    fraudulent_vendors = ["FakeShop", "ScamStore", "FraudMart"]
    channels = ["online", "in-store"]
    coupon_codes = ["SAVE10", "SAVE20", "FREESHIP", "WELCOME", "HOLIDAY50"]

    # Pools for names, emails, and phones
    first_names = [
        "Alice",
        "Bob",
        "Carol",
        "David",
        "Eva",
        "Frank",
        "Grace",
        "Henry",
        "Ivy",
        "John",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Wilson",
    ]
    domains = ["example.com", "test.com", "mail.com"]

    # Determine counts
    n_abuse = int(n * abuse_rate)
    n_non_abuse = n - n_abuse

    # Generate unique pools for non-abuse cases
    unique_names = [
        f"{random.choice(first_names)} {random.choice(last_names)}_{i}"
        for i in range(n_non_abuse)
    ]
    unique_emails = [
        f"{name.lower().replace(' ','.')}@{random.choice(domains)}"
        for name in unique_names
    ]
    unique_phones = [
        f"+27{random.randint(600000000, 699999999)}" for _ in range(n_non_abuse)
    ]

    # Generate pools for fraud duplicates
    dup_names = [
        f"{random.choice(first_names)} {random.choice(last_names)}"
        for _ in range(max(1, n_abuse // 3))
    ]
    dup_emails = [
        f"fraud{random.randint(1, 100)}@{random.choice(domains)}"
        for _ in range(max(1, n_abuse // 3))
    ]
    dup_phones = [
        f"+27{random.randint(600000000, 699999999)}"
        for _ in range(max(1, n_abuse // 3))
    ]

    rows = []
    for i in range(n):
        # base fields
        transaction_id = f"tx_{i+1:04d}"
        user_id = random.choice(user_ids)
        transaction_date = (
            datetime.now() - timedelta(days=random.randint(0, date_range_days))
        ).strftime("%Y-%m-%d")
        merchant = random.choice(merchants)
        channel = random.choice(channels)
        items_count = random.randint(1, 5)
        original_amount = round(random.uniform(20, 300), 2)
        coupon = random.choice(coupon_codes)

        # Decide abuse by index to ensure exact count
        abuse = 1 if i < n_abuse else 0

        # Assign user-level attributes
        if abuse:
            user_name = random.choice(dup_names)
            email = random.choice(dup_emails)
            phone_number = random.choice(dup_phones)
            vendor_name = random.choice(fraudulent_vendors)
            discount_amount = round(original_amount * random.uniform(0.5, 1.0), 2)
        else:
            user_name = unique_names.pop()
            email = unique_emails.pop()
            phone_number = unique_phones.pop()
            vendor_name = random.choice(merchants)
            discount_amount = round(original_amount * random.uniform(0.05, 0.3), 2)

        final_amount = round(original_amount - discount_amount, 2)

        rows.append(
            {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "user_name": user_name,
                "email": email,
                "phone_number": phone_number,
                "transaction_date": transaction_date,
                "merchant": merchant,
                "vendor_name": vendor_name,
                "channel": channel,
                "items_count": items_count,
                "original_amount": original_amount,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "coupon_code": coupon,
                "abuse": abuse,
            }
        )

    # Shuffle so abuse and non-abuse are mixed
    df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
    return df


# Generate and split
full_df = generate_coupon_abuse_dataset_with_user_info(150, abuse_rate=0.3)
train_df = full_df.sample(n=100, random_state=42).reset_index(drop=True)
test_df = full_df.drop(train_df.index).reset_index(drop=True)

# Save CSVs and JSON
full_df.to_csv("data/coupon_abuse_full_with_users.csv", index=False)
train_df.to_csv("data/train_coupon_abuse_with_users.csv", index=False)
test_df.to_csv("data/test_coupon_abuse_with_users.csv", index=False)
full_df.to_json("data/coupon_abuse_full_with_users.json", orient="records", lines=False)

# Display preview

# Print shapes
print(f"Full dataset in data shape: {full_df.shape}")
print(f"Training set in data shape: {train_df.shape}")
print(f"Test set in datashape: {test_df.shape}")
