#!/usr/bin/env python3
"""
Script de análisis de logs de seguridad

Este script proporciona herramientas para analizar los logs de seguridad generados
por el sistema de gestión de flota de vehículos.

Uso:
    python scripts/analyze_security_logs.py [opciones]

Opciones:
    --summary          : Resumen general de actividad
    --user-activity USER : Actividad de un usuario específico
    --failed-logins    : Intentos de login fallidos
    --suspicious       : Actividad sospechosa
    --api-performance  : Rendimiento de APIs
    --date-range START END : Filtrar por rango de fechas (YYYY-MM-DD)
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

class SecurityLogAnalyzer:
    """Analizador de logs de seguridad"""

    def __init__(self, log_file='security.log'):
        self.log_file = Path(log_file)
        self.logs = []

    def parse_logs(self):
        """Parsea los logs del archivo"""
        if not self.log_file.exists():
            print(f"Archivo de log no encontrado: {self.log_file}")
            return

        self.logs = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Parsear línea de log
                    log_entry = self._parse_log_line(line.strip())
                    if log_entry:
                        self.logs.append(log_entry)
                except Exception as e:
                    print(f"Error parseando línea: {e}")
                    continue

    def _parse_log_line(self, line):
        """Parsea una línea individual de log"""
        # Formato esperado: timestamp - level - [user_id] username@ip - operation - resource - details
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - \[([^\]]+)\] ([^@]+)@([^ ]+) - ([^-]+) - ([^-]+) - (.+)'

        match = re.match(pattern, line)
        if not match:
            return None

        timestamp_str, level, user_id, username, ip, operation, resource, details_str = match.groups()

        # Parsear detalles JSON si es posible
        details = {}
        try:
            details = json.loads(details_str)
        except:
            details = {'raw_details': details_str}

        return {
            'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
            'level': level,
            'user_id': user_id,
            'username': username,
            'ip_address': ip,
            'operation': operation.strip(),
            'resource': resource.strip(),
            'details': details
        }

    def get_summary(self, days=7):
        """Obtiene resumen general de actividad"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = [log for log in self.logs if log['timestamp'] > cutoff_date]

        summary = {
            'total_logs': len(recent_logs),
            'date_range': f"Últimos {days} días",
            'operations_by_type': Counter(log['operation'] for log in recent_logs),
            'users_active': len(set(log['username'] for log in recent_logs)),
            'failed_logins': len([log for log in recent_logs if 'LOGIN_FAILED' in log['operation']]),
            'successful_operations': len([log for log in recent_logs if log['level'] == 'INFO']),
            'errors_warnings': len([log for log in recent_logs if log['level'] in ['ERROR', 'WARNING']]),
        }

        return summary

    def get_user_activity(self, username, days=30):
        """Obtiene actividad de un usuario específico"""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_logs = [log for log in self.logs
                    if log['username'] == username and log['timestamp'] > cutoff_date]

        activity = {
            'username': username,
            'total_actions': len(user_logs),
            'operations': Counter(log['operation'] for log in user_logs),
            'resources_accessed': Counter(log['resource'] for log in user_logs),
            'last_activity': max((log['timestamp'] for log in user_logs), default=None),
            'ip_addresses': list(set(log['ip_address'] for log in user_logs)),
            'recent_actions': user_logs[-10:]  # Últimas 10 acciones
        }

        return activity

    def get_failed_logins(self, days=7):
        """Obtiene intentos de login fallidos"""
        cutoff_date = datetime.now() - timedelta(days=days)
        failed_logins = [log for log in self.logs
                        if 'LOGIN_FAILED' in log['operation'] and log['timestamp'] > cutoff_date]

        # Agrupar por IP y username
        failed_by_ip = defaultdict(list)
        failed_by_user = defaultdict(list)

        for log in failed_logins:
            failed_by_ip[log['ip_address']].append(log)
            failed_by_user[log['username']].append(log)

        return {
            'total_failed': len(failed_logins),
            'by_ip': {ip: len(logs) for ip, logs in failed_by_ip.items()},
            'by_user': {user: len(logs) for user, logs in failed_by_user.items()},
            'recent_failures': failed_logins[-5:]
        }

    def get_suspicious_activity(self, days=7):
        """Obtiene actividad sospechosa"""
        cutoff_date = datetime.now() - timedelta(days=days)
        suspicious = [log for log in self.logs
                     if log['level'] == 'WARNING' and 'SUSPICIOUS' in log['operation']
                     and log['timestamp'] > cutoff_date]

        return {
            'total_suspicious': len(suspicious),
            'by_type': Counter(log['operation'] for log in suspicious),
            'by_ip': Counter(log['ip_address'] for log in suspicious),
            'recent_suspicious': suspicious[-10:]
        }

    def get_api_performance(self, days=1):
        """Obtiene métricas de rendimiento de APIs"""
        cutoff_date = datetime.now() - timedelta(days=days)
        api_logs = [log for log in self.logs
                   if 'API_' in log['operation'] and log['timestamp'] > cutoff_date]

        performance = {
            'total_requests': len(api_logs),
            'by_endpoint': Counter(log['resource'] for log in api_logs),
            'response_codes': Counter(log['details'].get('response_code', 0) for log in api_logs),
            'avg_duration': sum(log['details'].get('duration_ms', 0) for log in api_logs) / len(api_logs) if api_logs else 0,
            'slow_requests': [log for log in api_logs if log['details'].get('duration_ms', 0) > 1000]
        }

        return performance

def print_summary(summary):
    """Imprime resumen de actividad"""
    print("📊 RESUMEN DE ACTIVIDAD DE SEGURIDAD")
    print("=" * 50)
    print(f"Período: {summary['date_range']}")
    print(f"Total de logs: {summary['total_logs']}")
    print(f"Usuarios activos: {summary['users_active']}")
    print(f"Logins fallidos: {summary['failed_logins']}")
    print(f"Operaciones exitosas: {summary['successful_operations']}")
    print(f"Errores/Advertencias: {summary['errors_warnings']}")
    print("\nOperaciones por tipo:")
    for op, count in summary['operations_by_type'].most_common(10):
        print(f"  {op}: {count}")

def print_user_activity(activity):
    """Imprime actividad de usuario"""
    print(f"👤 ACTIVIDAD DE USUARIO: {activity['username']}")
    print("=" * 50)
    print(f"Total de acciones: {activity['total_actions']}")
    print(f"Última actividad: {activity['last_activity']}")
    print(f"Direcciones IP: {', '.join(activity['ip_addresses'])}")

    print("\nOperaciones realizadas:")
    for op, count in activity['operations'].most_common():
        print(f"  {op}: {count}")

    print("\nRecursos accedidos:")
    for resource, count in activity['resources_accessed'].most_common():
        print(f"  {resource}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Análisis de logs de seguridad')
    parser.add_argument('--log-file', default='security.log', help='Archivo de log a analizar')
    parser.add_argument('--summary', action='store_true', help='Mostrar resumen general')
    parser.add_argument('--user-activity', help='Mostrar actividad de usuario específico')
    parser.add_argument('--failed-logins', action='store_true', help='Mostrar logins fallidos')
    parser.add_argument('--suspicious', action='store_true', help='Mostrar actividad sospechosa')
    parser.add_argument('--api-performance', action='store_true', help='Mostrar rendimiento de APIs')
    parser.add_argument('--days', type=int, default=7, help='Días hacia atrás para analizar')

    args = parser.parse_args()

    analyzer = SecurityLogAnalyzer(args.log_file)
    analyzer.parse_logs()

    if not analyzer.logs:
        print("No se encontraron logs para analizar.")
        return

    if args.summary:
        summary = analyzer.get_summary(args.days)
        print_summary(summary)

    if args.user_activity:
        activity = analyzer.get_user_activity(args.user_activity, args.days)
        print_user_activity(activity)

    if args.failed_logins:
        failed = analyzer.get_failed_logins(args.days)
        print(f"\n🔒 LOGINS FALLIDOS (últimos {args.days} días)")
        print("=" * 50)
        print(f"Total fallidos: {failed['total_failed']}")
        print("\nPor dirección IP:")
        for ip, count in failed['by_ip'].items():
            print(f"  {ip}: {count} intentos")

    if args.suspicious:
        suspicious = analyzer.get_suspicious_activity(args.days)
        print(f"\n⚠️  ACTIVIDAD SOSPECHOSA (últimos {args.days} días)")
        print("=" * 50)
        print(f"Total eventos: {suspicious['total_suspicious']}")
        print("\nPor tipo:")
        for tipo, count in suspicious['by_type'].items():
            print(f"  {tipo}: {count}")

    if args.api_performance:
        perf = analyzer.get_api_performance(args.days)
        print(f"\n🚀 RENDIMIENTO DE APIs (últimos {args.days} días)")
        print("=" * 50)
        print(f"Total de requests: {perf['total_requests']}")
        print(".2f")
        print(f"Requests lentos (>1s): {len(perf['slow_requests'])}")

        print("\nCódigos de respuesta:")
        for code, count in perf['response_codes'].items():
            print(f"  {code}: {count}")

if __name__ == '__main__':
    main()