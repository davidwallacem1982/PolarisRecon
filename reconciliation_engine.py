import polars as pl
import time
import os

def run_reconciliation():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 17 + "POLARIS RECON - ENGINE CORE" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    
    start_time = time.time()
    
    # 1. Carregar dados (SLA Check: I/O Speed)
    print("[*] Carregando conjuntos de dados massivos...")
    if not os.path.exists("data/external_file.csv") or not os.path.exists("data/internal_base.csv"):
        print("❌ ERRO: Arquivos de dados não encontrados.")
        print("💡 Sugestão: Execute 'python generate_data.py' primeiro.")
        return

    external_df = pl.read_csv("data/external_file.csv")
    internal_df = pl.read_csv("data/internal_base.csv")
    
    after_load = time.time()
    print(f"[*] I/O Concluído em {after_load - start_time:.4f}s")

    # 2. Outer Join para identificar orfandade
    print("[*] Executando Vectorized Outer Join (High Precision)...")
    reconciled = internal_df.join(
        external_df, 
        on="order_id", 
        how="outer", 
        suffix="_ext"
    )
    
    # 3. Categorização de Divergências
    print("[*] Aplicando Máscaras de Divergência e Orfandade...")
    
    # - Missing in External
    missing_in_ext = reconciled.filter(pl.col("external_id_ext").is_null())
    
    # - Missing in Internal
    missing_in_int = reconciled.filter(pl.col("external_id").is_null())
    
    # - Divergence in Quantity or Price
    matches = reconciled.filter(
        pl.col("external_id").is_not_null() & pl.col("external_id_ext").is_not_null()
    )
    
    divergences = matches.filter(
        (pl.col("quantity") != pl.col("quantity_ext")) | 
        (pl.col("unit_price") != pl.col("unit_price_ext"))
    )
    
    # 4. Geração de Relatório
    print("[*] Exportando relatórios detalhados para /reports...")
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    divergences.write_csv("reports/divergences.csv")
    missing_in_ext.write_csv("reports/missing_in_external.csv")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resumo Premium
    print("\n" + "    " + "📊 RESULTADOS DA CONCILIAÇÃO")
    print("    " + "─" * 40)
    print(f"    Total Processado:   {reconciled.height:,} registros")
    print(f"    Divergências:       {divergences.height:,}")
    print(f"    Orfandade (Ext):    {missing_in_ext.height:,}")
    print(f"    Orfandade (Int):    {missing_in_int.height:,}")
    print("    " + "─" * 40)
    print(f"    ⏱️  TEMPO TOTAL:   {total_time:.4f}s")
    print(f"    🎯  SLA STATUS:    {((total_time/1200)*100):.4f}% do limite (20 min)")
    print("    " + "─" * 40 + "\n")

if __name__ == "__main__":
    run_reconciliation()
