from django.db import models
import logging

from combustible.storage_backends import MediaStorage, upload_ticket_photo, optimize_image_for_storage

from equipo.models import Equipo
from operador.models import Operador

logger = logging.getLogger(__name__)

# Create your models here.


class Registro(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    numero_tiket = models.CharField(max_length=20, verbose_name="Numero ticket")
    idEquipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    idOperador = models.ForeignKey(Operador, on_delete=models.DO_NOTHING)
    Litros = models.DecimalField(max_digits=4,decimal_places=2, verbose_name="Cantidad de litros")
    costolitro = models.DecimalField(max_digits=4,decimal_places=2, verbose_name="Costo por litro")
    kilometraje = models.IntegerField(default=0, verbose_name="Kilometraje de Vehiculo")
    photo_tiket = models.ImageField(
        storage=MediaStorage(),
        upload_to=upload_ticket_photo,  # Función personalizada para generar rutas
        null=True,
        blank=True,
        verbose_name="Foto del ticket",
        help_text="Imagen del ticket de combustible"
    )

    def __str__(self) -> str:
        return f"Ticket {self.numero_tiket} - {self.idEquipo.placa}"
    
    def save(self, *args, **kwargs):
        # Optimizar imagen del ticket antes de guardar
        # if self.photo_tiket:
        #     try:
        #         # Optimización más agresiva para tickets (archivos más pequeños)
        #         optimized = optimize_image_for_storage(
        #             self.photo_tiket, 
        #             max_size=(1280, 960),  # Resolución más pequeña para tickets
        #             quality=75  # Calidad un poco menor
        #         )
        #         if optimized != self.photo_tiket:
        #             self.photo_tiket = optimized
        #             logger.info(f"🎫 Imagen del ticket {self.numero_tiket} optimizada")
        #     except Exception as e:
        #         logger.error(f"❌ Error optimizando imagen del ticket: {e}")
        
        super().save(*args, **kwargs)
        logger.info(f"💾 Registro guardado: {self.numero_tiket}")
    
    @property
    def total_costo(self):
        """Calcula el costo total del registro"""
        return self.Litros * self.costolitro
    
    @property
    def photo_url(self):
        """Obtiene la URL de la foto del ticket de manera segura"""
        if self.photo_tiket:
            try:
                return self.photo_tiket.url
            except Exception as e:
                logger.error(f"❌ Error obteniendo URL de foto: {e}")
                return None
        return None
    
    @property
    def photo_filename(self):
        """Obtiene el nombre del archivo de foto"""
        if self.photo_tiket:
            return self.photo_tiket.name.split('/')[-1]
        return None
    
    def delete_photo(self):
        """Elimina la foto del ticket de manera segura"""
        if self.photo_tiket:
            try:
                from combustible.storage_backends import delete_file_from_storage
                success = delete_file_from_storage(self.photo_tiket.name)
                if success:
                    self.photo_tiket = None
                    self.save(update_fields=['photo_tiket'])
                    logger.info(f"🗑️ Foto del ticket {self.numero_tiket} eliminada")
                return success
            except Exception as e:
                logger.error(f"❌ Error eliminando foto del ticket: {e}")
                return False
        return True

class ReporteGenerado(models.Model):
    """Modelo para tracking de reportes generados y almacenados"""
    
    TIPOS_REPORTE = [
        ('mensual', 'Reporte Mensual'),
        ('anual', 'Reporte Anual'),
        ('personalizado', 'Reporte Personalizado'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del reporte")
    tipo = models.CharField(max_length=20, choices=TIPOS_REPORTE, verbose_name="Tipo de reporte")
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(verbose_name="Fecha inicio del período")
    fecha_fin = models.DateField(verbose_name="Fecha fin del período")
    
    # Archivo Excel guardado en Spaces
    archivo_excel = models.FileField(
        upload_to='reportes/excel/',
        null=True,
        blank=True,
        verbose_name="Archivo Excel"
    )
    
    # Metadatos del reporte
    total_registros = models.PositiveIntegerField(default=0)
    total_litros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gastado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Estado del reporte
    enviado_por_email = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    destinatarios = models.JSONField(default=list, verbose_name="Lista de destinatarios")
    
    class Meta:
        verbose_name = "Reporte Generado"
        verbose_name_plural = "Reportes Generados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_generacion.strftime('%d/%m/%Y')}"
    
    @property
    def archivo_url(self):
        """Obtiene la URL del archivo Excel"""
        if self.archivo_excel:
            try:
                return self.archivo_excel.url
            except Exception:
                return None
        return None
    
    def marcar_como_enviado(self, destinatarios_list=None):
        """Marca el reporte como enviado por email"""
        from django.utils import timezone
        
        self.enviado_por_email = True
        self.fecha_envio = timezone.now()
        if destinatarios_list:
            self.destinatarios = destinatarios_list
        self.save(update_fields=['enviado_por_email', 'fecha_envio', 'destinatarios'])