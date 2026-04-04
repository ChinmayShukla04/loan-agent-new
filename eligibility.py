def check_eligibility(credit_score, income):
    if credit_score >= 750 and income >= 30000:
        return "Approved", "Strong credit profile"
    elif credit_score >= 650 and income >= 20000:
        return "Review", "Moderate risk"
    else:
        return "Rejected", "Low credit score or income"