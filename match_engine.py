# from data_loader import buyer_indexer, grant_indexer
# from models import SalesRepDropdownInput
# import math
# from datetime import datetime
# import numpy as np


# def build_rep_query(rep_input: SalesRepDropdownInput):
#     """
#     Builds a query from sales rep dropdown selections.
#     """
#     return f"{rep_input.agency_type} {rep_input.product_type} {rep_input.state}"

# def build_composite_buyer_query(buyer, rep_input):
#     """
#     Combines buyer profile and rep input into one string for semantic search.
#     """
#     buyer_fields = " ".join(str(v) for v in buyer.values())
#     return f"{buyer_fields} {rep_input.product_type} {rep_input.state}"

# def build_grant_query(grant):
#     """
#     Combines all meaningful grant fields into one string for embedding similarity.
#     """
#     grant_fields = " ".join(str(v) for v in grant.values())
#     return grant_fields

# def lexical_overlap(a, b):
#     a_tokens = set(a.lower().split())
#     b_tokens = set(b.lower().split())
#     if not a_tokens or not b_tokens:
#         return 0.0
#     return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


# def deadline_decay(deadline):
#     """Higher score when the deadline is closer."""
#     try:
#         d = datetime.strptime(deadline.strip(), "%Y-%m-%d")
#         days_left = (d - datetime.now()).days
#         if days_left <= 0:
#             return 0.0
        
#         return math.exp(-days_left / 120)
#     except Exception:
#         return 0.6  


# def get_ranked_matches_cosine(rep_input: SalesRepDropdownInput,
#                               top_k_buyers=5, top_k_grants=5):
#     """Hybrid semantic + metadata + lexical + geo scoring with tuned weights."""
#     rep_query = f"{rep_input.agency_type} {rep_input.product_type} {rep_input.state}"
#     buyers = buyer_indexer.search(rep_query, top_k=top_k_buyers)
#     seen, results = set(), []

    
#     W_BUYER, W_GRANT, W_LEX, W_DEADLINE, W_GEO = 0.30, 0.20, 0.30, 0.10, 0.10 

#     for buyer, buyer_score in buyers:
#         buyer_query = " ".join(str(v) for v in buyer.values()) + f" {rep_input.product_type} {rep_input.state}"
#         grants = grant_indexer.search(buyer_query, top_k=top_k_grants)

        
#         buyer_product_names = str(buyer.get("Product Name", "")).lower().split("/")
#         buyer_product_names = [p.strip() for p in buyer_product_names]
#         agency_type = str(buyer.get("Agency Type", "")).lower().strip()
#         keyword_terms = buyer_product_names + ([agency_type] if agency_type else [])

#         for grant, grant_score in grants:
#             key = (grant.get("Grant Program Name", ""), grant.get("Administering Agency", ""))
#             if key in seen:
#                 continue
#             seen.add(key)

#             gtext = " ".join(str(v) for v in grant.values())
#             lex = lexical_overlap(buyer_query, gtext)
#             ddl = deadline_decay(grant.get("Application Deadline", ""))
#             geo = 1.0 if rep_input.state.lower() in gtext.lower() else 0.7

            
#             keyword_boost = 0.0
#             matched_keywords = []

#             keyword_fields = [
#                 str(grant.get("Eligible Equipment/Expenses", "")),
#                 str(grant.get("Purpose", "")),
#                 str(grant.get("Focus Areas", "")),
#                 str(grant.get("Eligible Applicants", "")),
#             ]
#             keyword_text = " ".join(keyword_fields).lower()
#             for term in keyword_terms:
#                 if term and term in keyword_text:
#                     keyword_boost += 0.15
#                     matched_keywords.append(term)

           
#             raw = (W_BUYER * buyer_score +
#                    W_GRANT * grant_score +
#                    W_LEX * lex +
#                    W_DEADLINE * ddl +
#                    W_GEO * geo +
#                    keyword_boost)

            
#             conf = round((1 / (1 + math.exp(-4 * (raw - 0.45)))) * 100, 2)

        
#             conf = round(min(100, conf * (1 + 0.3 * ddl)), 2)

#             explanation = (
#                 f"Matched on {rep_input.product_type} for {rep_input.agency_type} in {rep_input.state}. "
#                 f"Buyer score={round(buyer_score,2)}, Grant score={round(grant_score,2)}, "
#                 f"Lexical overlap={round(lex,2)}, Deadline decay={round(ddl,2)}, Geo match={geo}, "
#                 f"Keyword boost={round(keyword_boost,2)}. "
#                 f"Weighted sum: {round(raw,3)}. "
#             )
#             if matched_keywords:
#                 explanation += f" Keyword boost for: {', '.join(matched_keywords)}."
#             else:
#                 explanation += " No keyword boost applied."

            
#             explanation += (
#                 f" Checked keyword terms: {keyword_terms}. "
#                 f"Grant fields used for matching: Eligible Equipment/Expenses, Purpose, Focus Areas, Eligible Applicants."
#             )

#             results.append({
#                 "grant_title": grant.get("Grant Program Name", "Unknown Program"),
#                 "description": grant.get("Purpose", "No Description"),
#                 "agency": grant.get("Administering Agency", "Unknown Agency"),
#                 "amount": grant.get("Award Amount Range", ""),
#                 "deadline": grant.get("Application Deadline", ""),
#                 "buyer_agency": buyer.get("Agency Name", "Unknown Agency"),
#                 "buyer_score": round(buyer_score * 100, 2),
#                 "grant_score": round(grant_score * 100, 2),
#                 "confidence_score": conf,
#                 "explanation": explanation
#             })

#     return sorted(results, key=lambda x: x["confidence_score"], reverse=True)

from data_loader import buyer_indexer, grant_indexer
from models import SalesRepDropdownInput
import math
from datetime import datetime
from rapidfuzz import fuzz


# ---------------------------
# Utility functions
# ---------------------------

def lexical_overlap(a: str, b: str) -> float:
    """Compute token overlap between buyer and grant text."""
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def deadline_decay(deadline: str) -> float:
    """Higher score when the deadline is closer (exponential decay)."""
    try:
        d = datetime.strptime(deadline.strip(), "%Y-%m-%d")
        days_left = (d - datetime.now()).days
        if days_left <= 0:
            return 0.0
        return math.exp(-days_left / 120)
    except Exception:
        return 0.5


def keyword_similarity(term: str, text: str) -> float:
    """Return fuzzy similarity (0–1) tolerant to plural/hyphen/spacing."""
    return fuzz.partial_ratio(term.lower(), text.lower()) / 100.0


# ---------------------------
# Core Matching Logic
# ---------------------------

def get_ranked_matches_cosine(rep_input: SalesRepDropdownInput,
                              top_k_buyers=5, top_k_grants=5):
    """
    Hybrid semantic + metadata + lexical + geo + keyword scoring
    with contextual fallback, dual-match amplification, and
    alignment filtering between rep query and buyer product terms.
    """

    rep_query = f"{rep_input.agency_type} {rep_input.product_type} {rep_input.state}"
    buyers = buyer_indexer.search(rep_query, top_k=top_k_buyers)
    seen, results = set(), []

    # Tuned weights
    W_BUYER, W_GRANT, W_LEX, W_DEADLINE, W_GEO = 0.20, 0.15, 0.25, 0.10, 0.15

    for buyer, buyer_score in buyers:
        buyer_query = " ".join(str(v) for v in buyer.values()) + f" {rep_input.product_type} {rep_input.state}"
        grants = grant_indexer.search(buyer_query, top_k=top_k_grants)

        # Extract contextual keyword terms
        buyer_product_names = [p.strip().lower()
                               for p in str(buyer.get("Product Name", "")).split("/")
                               if p.strip()]
        agency_type = str(buyer.get("Agency Type", "")).lower().strip()
        keyword_terms = buyer_product_names + ([agency_type] if agency_type else [])

        # 🔹 Filter buyer terms so they align with the rep query
        query_term = rep_input.product_type.lower()
        filtered_terms = []
        for term in keyword_terms:
            if fuzz.partial_ratio(term, query_term) / 100.0 >= 0.6 or query_term in term:
                filtered_terms.append(term)
        keyword_terms = list(set(filtered_terms + [query_term]))

        for grant, grant_score in grants:
            key = (grant.get("Grant Program Name", ""), grant.get("Administering Agency", ""))
            if key in seen:
                continue
            seen.add(key)

            gtext = " ".join(str(v) for v in grant.values())
            lex = lexical_overlap(buyer_query, gtext)
            ddl = deadline_decay(grant.get("Application Deadline", ""))
            geo = 1.0 if rep_input.state.lower() in gtext.lower() else 0.7

            # ---------------- Keyword Boost ----------------
            keyword_fields = [
                str(grant.get("Eligible Equipment/Expenses", "")),
                str(grant.get("Purpose", "")),
                str(grant.get("Focus Areas", "")),
                str(grant.get("Eligible Applicants", "")),
            ]
            keyword_text = " ".join(keyword_fields)
            keyword_boost, matched_keywords = 0.0, []
            grant_match, context_match = False, False

            for term in keyword_terms:
                sim = keyword_similarity(term, keyword_text)
                # strict fuzzy + literal presence
                if sim >= 0.85 and term.lower() in keyword_text.lower():
                    grant_match = True
                    matched_keywords.append(f"{term} ({round(sim,2)})")
                    keyword_boost += 0.25 * math.log1p(sim)

            # context-based fallback
            buyer_context = " ".join(str(v).lower() for v in buyer.values())
            if rep_input.product_type.lower() in buyer_context:
                context_match = True
                if grant_match:
                    keyword_boost += 0.15
                elif not grant_match:
                    keyword_boost = max(keyword_boost, 0.1)

            # sanity check: irrelevant keyword should not boost
            if matched_keywords and rep_input.product_type.lower() not in " ".join(matched_keywords).lower():
                keyword_boost *= 0.2

            if not grant_match and not context_match:
                keyword_boost = -0.1

            keyword_boost = max(-0.1, min(0.6, keyword_boost))

            # ---------------- Weighted Sum ----------------
            raw = (W_BUYER * buyer_score +
                   W_GRANT * grant_score +
                   W_LEX * lex +
                   W_DEADLINE * ddl +
                   W_GEO * geo +
                   keyword_boost)

            raw = min(raw, 0.6)  # avoid runaway 100%

            # ---------------- Confidence Score ----------------
            conf = (1 / (1 + math.exp(-10 * (raw - 0.4)))) * 100
            conf = round(min(100, conf * (1 + 0.4 * ddl)), 2)

            # ---------------- Explanation ----------------
            explanation = (
                f"Matched on {rep_input.product_type} for {rep_input.agency_type} in {rep_input.state}. "
                f"Buyer={buyer_score:.2f}, Grant={grant_score:.2f}, Lex={lex:.2f}, "
                f"Deadline={ddl:.2f}, Geo={geo}, KWBoost={keyword_boost:.2f}, Raw={raw:.3f}. "
            )
            if matched_keywords:
                explanation += f"Keywords matched: {matched_keywords}. "
            elif context_match:
                explanation += "No direct keyword match, but contextual boost applied. "
            else:
                explanation += "No keyword match detected (penalty applied). "

            explanation += "Grant fields checked: Eligible Equipment/Expenses, Purpose, Focus Areas, Eligible Applicants."

            results.append({
                "grant_title": grant.get("Grant Program Name", "Unknown Program"),
                "description": grant.get("Purpose", "No Description"),
                "agency": grant.get("Administering Agency", "Unknown Agency"),
                "amount": grant.get("Award Amount Range", ""),
                "deadline": grant.get("Application Deadline", ""),
                "buyer_agency": buyer.get("Agency Name", "Unknown Agency"),
                "buyer_score": round(buyer_score * 100, 2),
                "grant_score": round(grant_score * 100, 2),
                "confidence_score": conf,
                "explanation": explanation
            })

            print(f"[DEBUG] Raw={raw:.3f}, KWBoost={keyword_boost:.2f}, "
                  f"Lex={lex:.2f}, Geo={geo}, Conf={conf:.2f}, "
                  f"Context={context_match}, GrantMatch={grant_match}, "
                  f"Keywords={matched_keywords}")

    return sorted(results, key=lambda x: x["confidence_score"], reverse=True)
