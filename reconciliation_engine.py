import polars as pl
import time
import os

def run_reconciliation():
    print("Iniciando motor de conciliação (Polars)...")
    start_time = time.time()
    
    # 1. Carregar dados (SLA Check: I/O Speed)
    print("Carregando arquivos...")
    if not os.path.exists("data/external_file.csv") or not os.path.exists("data/internal_base.csv"):
        print("Erro: Arquivos de dados não encontrados. Rode o gerador de dados primeiro.")
        return

    external_df = pl.read_csv("data/external_file.csv")
    internal_df = pl.read_csv("data/internal_base.csv")
    
    after_load = time.time()
    print(f"Arquivos carregados em {after_load - start_time:.4f} segundos.")

    # 2. Outer Join para identificar orfandade
    print("Executando Outer Join...")
    reconciled = internal_df.join(
        external_df, 
        on="order_id", 
        how="outer", 
        suffix="_ext"
    )
    
    # 3. Categorização de Divergências
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
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    divergences.write_csv("reports/divergences.csv")
    missing_in_ext.write_csv("reports/missing_in_external.csv")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resumo
    print("\n" + "="*40)
    print("RESUMO DA CONCILIAÇÃO")
    print("="*40)
    print(f"Total registros processados: {reconciled.height}")
    print(f"Divergências encontradas: {divergences.height}")
    print(f"Faltantes no arquivo externo: {missing_in_ext.height}")
    print(f"Extras no arquivo externo: {missing_in_int.height}")
    print(f"Tempo total de execução: {total_time:.4f} segundos")
    print("-" * 40)
    print(f"SLA Máximo: 1.200 segundos (20 min)")
    print(f"SLA Atingido: {total_time:.4f} segundos ({(total_time/1200)*100:.2f}%)")
    print("="*40)

if __name__ == "__main__":
    run_reconciliation()
