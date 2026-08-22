---
license: cc0-1.0
task_categories:
- text-generation
- question-answering
- text-retrieval
language:
- en
tags:
- commercetxt
- e-commerce
- product-catalog
- ikea
- retail
- rag
- llm-optimization
- token-efficiency
- rag-benchmark
- structured-data
- synthetic
pretty_name: IKEA US CommerceTXT Dataset
size_categories:
- 10K<n<100K
---

# IKEA US - CommerceTXT Dataset

[![Standard](https://img.shields.io/badge/standard-stable-green.svg)](https://github.com/commercetxt/commercetxt/blob/main/spec/README.md)
[![AI Context](https://img.shields.io/badge/AI-Context-blue?logo=openai)](https://github.com/commercetxt/commercetxt/blob/main/CONTEXT.md)


**30,511 IKEA US products in CommerceTXT v1.0.1 format** - A token-optimized, human-readable alternative to JSON for e-commerce data.

## 📊 Dataset Statistics

| Metric | Value              |
|--------|--------------------|
| **Products** | 30,511             |
| **Categories** | 632                |
| **Format** | CommerceTXT v1.0.1 |
| **Data Date** | 2025-07-15         |
| **Token Savings** | 24% vs JSON       |
| **Tokens Saved** | 3.6M              |

## 🎯 What is CommerceTXT?

CommerceTXT is a lightweight, text-based protocol designed for AI/LLM consumption of e-commerce data. It eliminates JSON overhead while maintaining structure and readability.

**Key Benefits:**
- ✅ **24% fewer tokens** than JSON (3.6M saved including catalog structure)
- ✅ **Human-readable** - easy to debug and version control
- ✅ **AI-optimized** - clean format for RAG and LLM processing
- ✅ **Structured** - parseable with simple rules

## 📁 Dataset Structure

```
ikea-us-commercetxt/
├── commerce.txt                    # Root with @CATALOG (632 categories)
├── products/                       # 30,511 files organized by category
│   ├── frames/
│   │   ├── 00263858.txt
│   │   └── ...
│   ├── tables-and-desks/
│   │   └── ...
│   └── ... (632 category folders)
├── categories/                     # 632 category index files
│   ├── frames.txt
│   ├── tables-and-desks.txt
│   └── ...
```

## 🚀 Usage

### Load with datasets library

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("tsazan/ikea-us-commercetxt")

# Access files
commerce_txt = dataset['train'][0]['commerce.txt']
product_files = dataset['train'][0]['products']
```

### Direct file access

```python
# Read root catalog
with open("commerce.txt") as f:
    catalog = f.read()
    print(catalog)

# Read a product (note: products are organized by category)
with open("products/frames/00263858.txt") as f:
    product = f.read()
    print(product)

# Read a category index
with open("categories/frames.txt") as f:
    category = f.read()
    print(category)
```

### Parse with CommerceTXT parser

```python
from commercetxt import parse_file

# Parse product file (in category folder)
result = parse_file("products/frames/00263858.txt")

# Access structured data
product = result.directives.get('PRODUCT', {})
offer = result.directives.get('OFFER', {})

print(f"Product: {product.get('Name')}")
print(f"Price: ${offer.get('Price')}")
print(f"Brand: {product.get('Brand')}")
```

## 📝 File Format Example

```
# @PRODUCT
Name: KNOPPÄNG frame, black
SKU: 00263858
Brand: IKEA
LastUpdated: 2025-07-15T00:00:00Z
URL: https://www.ikea.com/us/en/p/knoppaeng-frame-black-00263858/
Category: Frames

# @OFFER
Price: 5.99
Currency: USD
Availability: InStock
Condition: New
TaxIncluded: False

# @SPECS
Materials: Wood
Dimensions: Width: 12", Height: 16"
Care: Wipe clean with a cloth

# @IMAGES
- https://www.ikea.com/us/en/images/products/knoppaeng-frame-black__0638237_pe698788_s5.jpg
```

## 💰 Token Efficiency

**Full Dataset Comparison (including catalog structure):**

>**Clarification:** Disclaimer section is not included in any of the token counts or savings calculations.

| Component | JSON Tokens | CommerceTXT Tokens | Savings |
|-----------|-------------|-------------------|---------|
| **Products (30,511)** | 14,894,623 | 10,212,452 | 31.44% |
| **Categories (632)** | N/A* | 1,073,051 | - |
| **Root Catalog** | N/A* | 11,180 | - |
| **TOTAL** | **14,894,623** | **11,296,683** | **24.16%** |

\* JSON has no built-in catalog structure (requires separate database/index)


**Per Product Average:**
- JSON: 488 tokens/product
- CommerceTXT: 370 tokens/product (including catalog overhead)
- **Savings: 118 tokens/product (24%)**

**Cost Impact (GPT-4o at $2.50/1M input tokens):**
- 1 query/day: **$269/month saved**
- 10 queries/day: **$2,690/month saved**
- 100 queries/day: **$26,900/month saved**

> **Note:** CommerceTXT includes structured navigation via `@CATALOG` and category files, which JSON lacks. Categories list all products, adding ~1.08M tokens. Even with this catalog overhead, CommerceTXT saves **3.6M tokens (24%)**!


## 🔍 Use Cases

### 1. RAG (Retrieval-Augmented Generation)
```python
# Load products into vector database
# Query: "Find affordable black frames"
# Retrieve relevant .txt files
# Pass to LLM for response generation
```

### 2. Product Search
```python
# Semantic search across 30K products
# Token-efficient context for LLM ranking
# Real-time price/availability lookup
```

### 3. AI Shopping Assistant
```python
# Natural language product queries
# Compare products efficiently
# Generate recommendations
```

## 📊 Token Savings Distribution

**Product-level savings distribution (30,511 products):**

When comparing individual products (JSON → CommerceTXT), before adding catalog overhead:

```
  0-10%:    111 products (0.4%)
 10-20%:  5,934 products (19.4%)
 20-30%: 10,018 products (32.8%)  ← Most common
 30-40%: 10,433 products (34.2%)  ← Most common
 40-50%:  3,239 products (10.6%)
   >50%:    776 products (2.5%)
```

**Product average:** ~31% savings per product  
**Dataset total (with catalog):** 24% savings overall

> **Note:** Individual products save ~31% on average, but the full dataset (including 632 category files with product listings) saves 24% overall. The catalog structure adds navigation value that JSON lacks.

## ⚖️ Legal & Disclaimer

**Important:** This is an **unofficial research dataset** for demonstrating CommerceTXT protocol.

- ❌ **NOT affiliated** with IKEA Systems B.V.
- ⚠️ **Static snapshot** from July 2025 - data may be outdated
- 🔒 **Research/educational use only** - not for commercial purposes
- ™️ IKEA® is a registered trademark of Inter IKEA Systems B.V.

**No warranty provided. Use at your own risk.**

## 📚 Resources

- **CommerceTXT:** [github.com/commercetxt/commercetxt](https://github.com/commercetxt/commercetxt)
- **Parser (Python):** `pip install commercetxt`
- **Original Data:** Based on IKEA US scrape by Jeffrey Zhou ([HF Dataset](https://huggingface.co/datasets/jeffreyszhou/ikea-us-products-2025))

## 🛠️ Generation

This dataset was generated from [IKEA US Product Dataset (July 2025](https://huggingface.co/datasets/jeffreyszhou/ikea-us-products-2025) by converting it to CommerceTXT v1.0.1 format.

**Conversion process:**
1. Parsed JSON from [source dataset](https://huggingface.co/datasets/jeffreyszhou/ikea-us-products-2025)
2. Extracted clean product names (removed measurements, IKEA US suffix)
3. Organized products into 632 category folders
4. Converted to CommerceTXT structured format
5. Generated category index files with full product listings
6. Created root @CATALOG with all 632 categories
7. Validated all 30,511 product files for spec compliance


## 📜 Citation

If you use this dataset, please cite:

```bibtex
@dataset{ikea_us_commercetxt_2025,
  title = {IKEA US CommerceTXT Dataset},
  author = {Tsanko Zanov},
  year = {2026},
  url = {https://huggingface.co/datasets/tsazan/ikea-us-commercetxt}
}
```

**Original data source:**
```bibtex
@misc{ikea_us_products_2025,
  title = {IKEA US Product Dataset (July 2025)},
  author = {Jeffrey Zhou},
  year = {2025},
  url = {https://huggingface.co/datasets/jeffreyszhou/ikea-us-products-2025}
}
```

## ⚖️ Legal & Disclaimer

**License:** CC0 1.0 (Public Domain Dedication)

**Important:** This is an **unofficial research dataset** for demonstrating CommerceTXT protocol.


## 📬 Contact

- **Issues/Questions:** [GitHub Issues](https://github.com/commercetxt/commercetxt/issues)
- **Protocol Spec:** [github.com/commercetxt/commercetxt](https://github.com/commercetxt/commercetxt/tree/main/spec)

---

**Built with ❤️ for the AI & e-commerce community**