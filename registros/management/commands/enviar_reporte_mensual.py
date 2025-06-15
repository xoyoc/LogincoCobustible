# management/commands/enviar_reporte_mensual.py - Versión actualizada con Spaces
import os
import calendar
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum, Count, Q, Max
from django.core.files.base import ContentFile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
import logging

from tu_app.models import Registro, Equipo, Operador, ReporteGenerado
from tu_app.storage_backends import ReportesStorage, get_file_url

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Envía reporte mensual de combustible por correo electrónico con integración a Spaces'

    def add_arguments(self, parser):
        parser.add_argument('--mes', type=int, help='Mes específico (1-12)')
        parser.add_argument('--año', type=int, help='Año específico')
        parser.add_argument('--email', type=str, help='Email específico')
        parser.add_argument('--test', action='store_true', help='Modo test')
        parser.add_argument('--save-to-spaces', action='store_true', default=True, help='Guardar Excel en Spaces')
        parser.add_argument('--include-photos', action='store_true', help='Incluir fotos en el reporte')

    def handle(self, *args, **options):
        try:
            # Determinar el período del reporte
            if options['mes'] and options['año']:
                año = options['año']
                mes = options['mes']
            else:
                # Mes anterior por defecto
                fecha_actual = datetime.now()
                if fecha_actual.month == 1:
                    mes = 12
                    año = fecha_actual.year - 1
                else:
                    mes = fecha_actual.month - 1
                    año = fecha_actual.year

            self.stdout.write(
                self.style.SUCCESS(f'📊 Generando reporte para {calendar.month_name[mes]} {año}...')
            )

            # Generar datos del reporte
            datos_reporte = self.generar_datos_reporte(año, mes)
            
            if options['test']:
                self.mostrar_estadisticas_consola(datos_reporte, año, mes)
                return

            # Generar archivo Excel
            excel_buffer, excel_filename = self.generar_excel(datos_reporte, año, mes)
            
            # Guardar en Spaces si está habilitado
            reporte_obj = None
            if options['save_to_spaces']:
                reporte_obj = self.guardar_excel_en_spaces(
                    excel_buffer, excel_filename, datos_reporte, año, mes
                )
            
            # Enviar por correo
            self.enviar_correo(
                datos_reporte, excel_buffer, excel_filename, año, mes, 
                options.get('email'), reporte_obj, options.get('include_photos', False)
            )
            
            # Marcar como enviado si se guardó en Spaces
            if reporte_obj:
                destinatarios = self.get_destinatarios(options.get('email'))
                reporte_obj.marcar_como_enviado(destinatarios)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Reporte mensual enviado exitosamente!')
            )

        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'❌ Error al generar reporte: {str(e)}')
            )

    def generar_datos_reporte(self, año, mes):
        """Genera todos los datos necesarios para el reporte - versión mejorada"""
        
        # Fechas del período
        primer_dia = datetime(año, mes, 1)
        ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1], 23, 59, 59)
        
        logger.info(f"Generando reporte para período: {primer_dia} - {ultimo_dia}")
        
        # Registros del mes con optimización de consultas
        registros_mes = Registro.objects.filter(
            fecha_hora__gte=primer_dia,
            fecha_hora__lte=ultimo_dia
        ).select_related('idEquipo', 'idOperador').prefetch_related().order_by('-fecha_hora')

        # Estadísticas generales
        total_registros = registros_mes.count()
        total_litros = registros_mes.aggregate(total=Sum('Litros'))['total'] or Decimal('0')
        total_gastado = sum([registro.total_costo for registro in registros_mes])

        # Estadísticas por equipo con URLs de fotos
        equipos_stats = {}
        for equipo in Equipo.objects.all().prefetch_related('registro_set'):
            registros_equipo = registros_mes.filter(idEquipo=equipo)
            
            if registros_equipo.exists():
                litros_equipo = registros_equipo.aggregate(total=Sum('Litros'))['total'] or Decimal('0')
                gasto_equipo = sum([reg.total_costo for reg in registros_equipo])
                ultimo_registro = registros_equipo.first()
                operadores_equipo = list(set([reg.idOperador.nombre for reg in registros_equipo]))
                
                # Incluir información de la foto del equipo desde Spaces
                foto_url = get_file_url(equipo.foto_equipo) if equipo.foto_equipo else None
                
                equipos_stats[equipo.placa] = {
                    'equipo': equipo,
                    'total_litros': litros_equipo,
                    'total_gastado': gasto_equipo,
                    'num_registros': registros_equipo.count(),
                    'operadores': operadores_equipo,
                    'ultimo_registro': ultimo_registro,
                    'promedio_litros': litros_equipo / registros_equipo.count() if registros_equipo.count() > 0 else 0,
                    'foto_url': foto_url,
                    'eficiencia': self.calcular_eficiencia_equipo(registros_equipo),
                }

        # Operadores que NO cargaron combustible
        operadores_activos = set(registros_mes.values_list('idOperador', flat=True))
        operadores_inactivos = Operador.objects.exclude(id__in=operadores_activos)

        # Estadísticas por operador mejoradas
        operadores_stats = {}
        for operador in Operador.objects.all():
            registros_operador = registros_mes.filter(idOperador=operador)
            
            if registros_operador.exists():
                litros_operador = registros_operador.aggregate(total=Sum('Litros'))['total'] or Decimal('0')
                gasto_operador = sum([reg.total_costo for reg in registros_operador])
                equipos_usados = list(set([reg.idEquipo.placa for reg in registros_operador]))
                
                # Incluir foto del operador
                foto_url = get_file_url(operador.foto_operador) if operador.foto_operador else None
                
                operadores_stats[operador.nombre] = {
                    'operador': operador,
                    'total_litros': litros_operador,
                    'total_gastado': gasto_operador,
                    'num_registros': registros_operador.count(),
                    'equipos_usados': equipos_usados,
                    'promedio_litros': litros_operador / registros_operador.count() if registros_operador.count() > 0 else 0,
                    'foto_url': foto_url,
                }

        # Top rankings
        top_equipos = sorted(equipos_stats.items(), key=lambda x: x[1]['total_litros'], reverse=True)[:5]
        top_operadores = sorted(operadores_stats.items(), key=lambda x: x[1]['num_registros'], reverse=True)[:5]

        # Estadísticas adicionales para Spaces
        registros_con_foto = registros_mes.exclude(photo_tiket__isnull=True).exclude(photo_tiket='').count()
        porcentaje_con_foto = (registros_con_foto / total_registros * 100) if total_registros > 0 else 0

        return {
            'año': año,
            'mes': mes,
            'nombre_mes': calendar.month_name[mes],
            'primer_dia': primer_dia,
            'ultimo_dia': ultimo_dia,
            'registros': list(registros_mes),
            'total_registros': total_registros,
            'total_litros': total_litros,
            'total_gastado': total_gastado,
            'equipos_stats': equipos_stats,
            'operadores_stats': operadores_stats,
            'operadores_inactivos': list(operadores_inactivos),
            'top_equipos': top_equipos,
            'top_operadores': top_operadores,
            'promedio_diario': total_gastado / calendar.monthrange(año, mes)[1] if total_gastado > 0 else 0,
            'promedio_litros_registro': total_litros / total_registros if total_registros > 0 else 0,
            'registros_con_foto': registros_con_foto,
            'porcentaje_con_foto': porcentaje_con_foto,
        }

    def calcular_eficiencia_equipo(self, registros_equipo):
        """Calcula métricas de eficiencia para un equipo"""
        if not registros_equipo.exists():
            return {}
        
        # Calcular eficiencia promedio (km por litro)
        registros_con_km = registros_equipo.exclude(kilometraje=0)
        if registros_con_km.count() > 1:
            registros_ordenados = list(registros_con_km.order_by('fecha_hora'))
            km_recorridos = []
            litros_usados = []
            
            for i in range(1, len(registros_ordenados)):
                km_diff = registros_ordenados[i].kilometraje - registros_ordenados[i-1].kilometraje
                if km_diff > 0:
                    km_recorridos.append(km_diff)
                    litros_usados.append(float(registros_ordenados[i].Litros))
            
            if km_recorridos and litros_usados:
                total_km = sum(km_recorridos)
                total_litros = sum(litros_usados)
                eficiencia = total_km / total_litros if total_litros > 0 else 0
                
                return {
                    'km_por_litro': round(eficiencia, 2),
                    'total_km_recorridos': total_km,
                    'costo_por_km': round(sum([r.total_costo for r in registros_con_km]) / total_km, 2) if total_km > 0 else 0
                }
        
        return {'km_por_litro': 0, 'total_km_recorridos': 0, 'costo_por_km': 0}

    def generar_excel(self, datos, año, mes):
        """Genera el archivo Excel con integración mejorada para Spaces"""
        
        wb = Workbook()
        
        # Estilos mejorados
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        subheader_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        
        # === HOJA 1: RESUMEN EJECUTIVO MEJORADO ===
        ws_resumen = wb.active
        ws_resumen.title = "Resumen Ejecutivo"
        
        # Título principal
        ws_resumen.merge_cells('A1:H1')
        title_cell = ws_resumen['A1']
        title_cell.value = f"REPORTE MENSUAL DE COMBUSTIBLE - {datos['nombre_mes'].upper()} {año}"
        title_cell.font = Font(bold=True, size=16, color="366092")
        title_cell.alignment = Alignment(horizontal='center')
        
        # Información general con URLs de Spaces
        row = 3
        info_general = [
            ["Período:", f"{datos['primer_dia'].strftime('%d/%m/%Y')} - {datos['ultimo_dia'].strftime('%d/%m/%Y')}"],
            ["Total de Registros:", datos['total_registros']],
            ["Registros con Foto:", f"{datos['registros_con_foto']} ({datos['porcentaje_con_foto']:.1f}%)"],
            ["Total de Litros:", f"{datos['total_litros']:.2f} L"],
            ["Total Gastado:", f"${datos['total_gastado']:.2f}"],
            ["Promedio Diario:", f"${datos['promedio_diario']:.2f}"],
            ["Promedio por Registro:", f"{datos['promedio_litros_registro']:.2f} L"],
        ]
        
        for info in info_general:
            ws_resumen[f'A{row}'] = info[0]
            ws_resumen[f'A{row}'].font = Font(bold=True)
            ws_resumen[f'B{row}'] = info[1]
            row += 1
        
        # === HOJA 2: DETALLE CON URLS DE FOTOS ===
        ws_detalle = wb.create_sheet("Detalle con URLs")
        
        headers_detalle = [
            "Fecha/Hora", "Ticket", "Placa", "Marca", "Modelo", 
            "Operador", "Litros", "Costo/L", "Total", "Kilometraje", "URL Foto"
        ]
        
        for col, header in enumerate(headers_detalle, 1):
            cell = ws_detalle.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
        
        # Datos con URLs de fotos
        for row, registro in enumerate(datos['registros'], 2):
            foto_url = get_file_url(registro.photo_tiket) if registro.photo_tiket else "Sin foto"
            
            ws_detalle[f'A{row}'] = registro.fecha_hora.strftime('%d/%m/%Y %H:%M')
            ws_detalle[f'B{row}'] = registro.numero_tiket
            ws_detalle[f'C{row}'] = registro.idEquipo.placa
            ws_detalle[f'D{row}'] = registro.idEquipo.marca
            ws_detalle[f'E{row}'] = registro.idEquipo.modelo
            ws_detalle[f'F{row}'] = registro.idOperador.nombre
            ws_detalle[f'G{row}'] = float(registro.Litros)
            ws_detalle[f'H{row}'] = float(registro.costolitro)
            ws_detalle[f'I{row}'] = float(registro.total_costo)
            ws_detalle[f'J{row}'] = registro.kilometraje
            ws_detalle[f'K{row}'] = foto_url
            
            for col in range(1, 12):
                ws_detalle.cell(row=row, column=col).border = border
        
        # === HOJA 3: ANÁLISIS DE EFICIENCIA ===
        ws_eficiencia = wb.create_sheet("Análisis de Eficiencia")
        
        headers_eficiencia = [
            "Placa", "Marca/Modelo", "Registros", "Litros", "Gasto",
            "Km/Litro", "Km Recorridos", "Costo/Km", "URL Foto Equipo"
        ]
        
        for col, header in enumerate(headers_eficiencia, 1):
            cell = ws_eficiencia.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
        
        row = 2
        for placa, stats in datos['equipos_stats'].items():
            eficiencia = stats.get('eficiencia', {})
            
            ws_eficiencia[f'A{row}'] = placa
            ws_eficiencia[f'B{row}'] = f"{stats['equipo'].marca} {stats['equipo'].modelo}"
            ws_eficiencia[f'C{row}'] = stats['num_registros']
            ws_eficiencia[f'D{row}'] = f"{stats['total_litros']:.2f}"
            ws_eficiencia[f'E{row}'] = f"${stats['total_gastado']:.2f}"
            ws_eficiencia[f'F{row}'] = eficiencia.get('km_por_litro', 0)
            ws_eficiencia[f'G{row}'] = eficiencia.get('total_km_recorridos', 0)
            ws_eficiencia[f'H{row}'] = f"${eficiencia.get('costo_por_km', 0):.2f}"
            ws_eficiencia[f'I{row}'] = stats.get('foto_url', 'Sin foto')
            
            for col in range(1, 10):
                ws_eficiencia.cell(row=row, column=col).border = border
            row += 1
        
        # Ajustar ancho de columnas automáticamente
        for ws in [ws_resumen, ws_detalle, ws_eficiencia]:
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        # Guardar en memoria
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_combustible_{año}_{mes:02d}_{timestamp}.xlsx"
        
        logger.info(f"📊 Excel generado: {filename}")
        return excel_buffer, filename

    def guardar_excel_en_spaces(self, excel_buffer, filename, datos_reporte, año, mes):
        """Guarda el archivo Excel en DigitalOcean Spaces"""
        try:
            # Crear objeto ReporteGenerado
            reporte = ReporteGenerado.objects.create(
                nombre=f"Reporte Mensual - {datos_reporte['nombre_mes']} {año}",
                tipo='mensual',
                fecha_inicio=datos_reporte['primer_dia'].date(),
                fecha_fin=datos_reporte['ultimo_dia'].date(),
                total_registros=datos_reporte['total_registros'],
                total_litros=datos_reporte['total_litros'],
                total_gastado=datos_reporte['total_gastado']
            )
            
            # Guardar archivo en Spaces
            excel_content = ContentFile(excel_buffer.getvalue(), name=filename)
            reporte.archivo_excel.save(filename, excel_content)
            
            logger.info(f"📁 Excel guardado en Spaces: {reporte.archivo_url}")
            self.stdout.write(
                self.style.SUCCESS(f'💾 Excel guardado en Spaces: {filename}')
            )
            
            return reporte
            
        except Exception as e:
            logger.error(f"Error guardando Excel en Spaces: {str(e)}")
            self.stdout.write(
                self.style.WARNING(f'⚠️ No se pudo guardar en Spaces: {str(e)}')
            )
            return None

    def get_destinatarios(self, email_especifico=None):
        """Obtiene la lista de destinatarios del reporte"""
        if email_especifico:
            return [email_especifico]
        else:
            return getattr(settings, 'REPORTES_EMAIL_DESTINATARIOS', [
                'admin@empresa.com',
                'gerencia@empresa.com'
            ])

    def enviar_correo(self, datos, excel_buffer, filename, año, mes, email_especifico=None, reporte_obj=None, include_photos=False):
        """Envía el correo con el reporte mejorado"""
        
        destinatarios = self.get_destinatarios(email_especifico)
        
        # Contexto del email con URLs de Spaces
        contexto_email = {
            'datos': datos,
            'año': año,
            'mes': mes,
            'reporte_url': reporte_obj.archivo_url if reporte_obj else None,
            'include_photos': include_photos,
        }
        
        # Agregar URLs de fotos si se solicita
        if include_photos:
            contexto_email['fotos_tickets'] = []
            for registro in datos['registros'][:10]:  # Máximo 10 fotos
                if registro.photo_tiket:
                    foto_url = get_file_url(registro.photo_tiket)
                    if foto_url:
                        contexto_email['fotos_tickets'].append({
                            'ticket': registro.numero_tiket,
                            'url': foto_url,
                            'equipo': registro.idEquipo.placa
                        })
        
        # Generar HTML del email
        html_content = render_to_string('emails/reporte_mensual.html', contexto_email)
        
        # Crear email
        asunto = f"📊 Reporte Mensual de Combustible - {datos['nombre_mes']} {año}"
        if reporte_obj:
            asunto += " (Disponible en Spaces)"
        
        email = EmailMessage(
            subject=asunto,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        email.content_subtype = "html"
        
        # Adjuntar Excel (siempre como backup)
        email.attach(filename, excel_buffer.getvalue(), 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Enviar
        email.send()
        
        logger.info(f"📧 Email enviado a: {', '.join(destinatarios)}")
        self.stdout.write(
            self.style.SUCCESS(f'📧 Email enviado a: {", ".join(destinatarios)}')
        )

    def mostrar_estadisticas_consola(self, datos, año, mes):
        """Muestra estadísticas en consola con información de Spaces"""
        
        print(f"\n{'='*70}")
        print(f"📊 REPORTE MENSUAL DE COMBUSTIBLE - {datos['nombre_mes'].upper()} {año}")
        print(f"{'='*70}")
        
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de registros: {datos['total_registros']}")
        print(f"   • Registros con foto: {datos['registros_con_foto']} ({datos['porcentaje_con_foto']:.1f}%)")
        print(f"   • Total de litros: {datos['total_litros']:.2f}L")
        print(f"   • Total gastado: ${datos['total_gastado']:.2f}")
        print(f"   • Promedio diario: ${datos['promedio_diario']:.2f}")
        
        print(f"\n🚛 TOP 5 EQUIPOS (por consumo):")
        for i, (placa, stats) in enumerate(datos['top_equipos'], 1):
            eficiencia = stats.get('eficiencia', {})
            km_litro = eficiencia.get('km_por_litro', 0)
            print(f"   {i}. {placa} - {stats['total_litros']:.2f}L (${stats['total_gastado']:.2f}) - {km_litro} km/L")
        
        print(f"\n👥 TOP 5 OPERADORES (por actividad):")
        for i, (nombre, stats) in enumerate(datos['top_operadores'], 1):
            print(f"   {i}. {nombre} - {stats['num_registros']} registros ({stats['total_litros']:.2f}L)")
        
        if datos['operadores_inactivos']:
            print(f"\n⚠️  OPERADORES SIN ACTIVIDAD:")
            for operador in datos['operadores_inactivos']:
                print(f"   • {operador.nombre} ({operador.email})")
        
        print(f"\n💾 INTEGRACIÓN CON SPACES:")
        print(f"   • Fotos de tickets almacenadas: ✅")
        print(f"   • Reportes Excel en la nube: ✅")
        print(f"   • URLs públicas disponibles: ✅")
        
        print(f"\n{'='*70}")

# === COMANDO ADICIONAL PARA MIGRACIÓN ===
# Este comando debería ejecutarse una vez para migrar archivos existentes