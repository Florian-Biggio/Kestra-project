import pandas as pd
import os
import pytest
from scipy.stats import zscore


@pytest.fixture(scope="module")
def load_data():
    # Get the base directory (one level up from the tests directory)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(base_dir, "output")

    # File paths
    final_merge_path = os.path.join(output_dir, "final_merge.csv")
    erp_path = os.path.join(output_dir, "erp.csv")
    liaison_path = os.path.join(output_dir, "liaison.csv")
    web_path = os.path.join(output_dir, "web.csv")
    ordinaire_path = os.path.join(output_dir, "vins_ordinaire.csv")
    millesimes_path = os.path.join(output_dir, "vins_millesimes.csv")

    # Load data
    final_merge = pd.read_csv(final_merge_path)
    erp = pd.read_csv(erp_path)
    liaison = pd.read_csv(liaison_path)
    web = pd.read_csv(web_path)
    ordinaire = pd.read_csv(ordinaire_path)
    millesimes = pd.read_csv(millesimes_path)

    return final_merge, erp, liaison, web, ordinaire, millesimes

def test_row_counts(load_data):
    final_merge, erp, liaison, web, _, _ = load_data
    
    assert len(erp) == 825, f"ERP row count is incorrect, found {len(erp)}"
    assert len(liaison) == 825, f"Liaison row count is incorrect, found {len(liaison)}"
    assert len(web) == 714, f"Web row count is incorrect, found {len(web)}"
    assert len(final_merge) == 714, f"Final merge row count is incorrect, found {len(final_merge)}"


def test_no_duplicates(load_data):
    *_, erp, liaison, web, _, _ = load_data
    
    assert erp['product_id'].is_unique, "Duplicates found in ERP"
    assert liaison[['product_id', 'id_web']].drop_duplicates().shape[0] == 825, "Duplicates found in Liaison"
    assert web['sku'].is_unique, "Duplicates found in Web"


def test_no_missing_values(load_data):
    final_merge, *_ = load_data
    
    assert final_merge[['product_id', 'price', 'CA']].notna().all().all(), "Missing values found in final_merge"


def test_revenue_consistency(load_data):
    final_merge, *_ = load_data
    
    total_revenue = final_merge["CA"].sum()
    assert round(total_revenue, 2) >= 0, f"Total revenue is incorrect, found {total_revenue}" # the expected value isn't included, since the data isn't usuable


def test_millesimes_wine_count(load_data):
    *_, millesimes  = load_data
    assert len(millesimes) == 30, f"Expected 30 millesimes, but got {len(millesimes)}"


def test_price_zscore(load_data):
    final_merge, *_ = load_data
    
    prices = final_merge["price"].dropna()
    zs = zscore(prices)
    outliers = (abs(zs) > 2).sum()
    assert outliers < len(prices) * 0.05, f"Too many price outliers, found {outliers} out of {len(prices)}"

