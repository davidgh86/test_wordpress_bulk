import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos del archivo CSV
file_path = 'report/report.csv'
data = pd.read_csv(file_path)

# Análisis de datos básicos
print("Datos generales:")
print(data.describe())

# Métricas adicionales
failed_tests = data['Failed'].sum()
total_tests = len(data)
avg_time = data['Time'].mean()
avg_retries = data['Retries'].mean()

print("\nResumen:")
print(f"Total de tests: {total_tests}")
print(f"Tests fallidos: {failed_tests}")
print(f"Tiempo promedio de ejecución (ms): {avg_time:.2f}")
print(f"Promedio de reintentos: {avg_retries:.2f}")

# Gráfico 1: Distribución del tiempo de ejecución
plt.figure(figsize=(10, 6))
plt.hist(data['Time'], bins=10, edgecolor='black')
plt.title('Distribución del Tiempo de Ejecución')
plt.xlabel('Tiempo (ms)')
plt.ylabel('Número de Tests')
plt.grid(axis='y')
plt.show()

# Gráfico 2: Número de reintentos por test
plt.figure(figsize=(10, 6))
plt.bar(data['Test Case'], data['Retries'], color='orange')
plt.xticks(rotation=90)
plt.title('Número de Reintentos por Test')
plt.xlabel('Caso de Test')
plt.ylabel('Número de Reintentos')
plt.grid(axis='y')
plt.show()

# Gráfico 3: Tiempo de ejecución vs. Número de reintentos
plt.figure(figsize=(10, 6))
plt.scatter(data['Retries'], data['Time'], color='green')
plt.title('Tiempo de Ejecución vs. Número de Reintentos')
plt.xlabel('Número de Reintentos')
plt.ylabel('Tiempo de Ejecución (ms)')
plt.grid()
plt.show()

# Gráfico 4: Comparativa de tiempos entre tests fallidos y exitosos
plt.figure(figsize=(10, 6))
plt.boxplot([data[data['Failed'] == False]['Time'], data[data['Failed'] == True]['Time']], labels=['Exitosos', 'Fallidos'])
plt.title('Comparativa de Tiempo de Ejecución entre Tests Exitosos y Fallidos')
plt.ylabel('Tiempo de Ejecución (ms)')
plt.grid()
plt.show()

# Gráfico 5: Tiempo de ejecución de cada test
plt.figure(figsize=(12, 6))
plt.plot(data['Test Case'], data['Time'], marker='o', color='b')
plt.xticks(rotation=90)
plt.title('Tiempo de Ejecución de Cada Test')
plt.xlabel('Caso de Test')
plt.ylabel('Tiempo de Ejecución (ms)')
plt.grid()
plt.show()
