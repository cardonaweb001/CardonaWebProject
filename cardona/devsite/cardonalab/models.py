from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
from django.core.exceptions import ValidationError

import re

### Generic Relations

def _file_upload_location(instance, filename):
    return '%s/%s/%s' % (instance.content_object._meta.object_name, instance.content_object.id, filename)

class File(models.Model):
    file = models.FileField(upload_to=_file_upload_location)
    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.file.name

class Bookmark(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

### Base class for models that record creator info

class BaseModel(models.Model):
    creator = models.ForeignKey(User, models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Declares this model as an abstract class; no table is created in database for this class
    class Meta:
        abstract = True

### Main models

class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "         Manufacturers" # Spaces are a hack to change the order on admin page

class StorageLocation(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "        Storage Locations"

class Chemical(BaseModel):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=1)
    number = models.IntegerField(editable=False)
    manufacturer = models.ForeignKey(Manufacturer, models.SET_NULL, null=True)
    location = models.ForeignKey(StorageLocation, models.SET_NULL, null=True)
    in_stock = models.BooleanField(default=True)
    msds = models.URLField('Link to MSDS', blank=True)
    notes = models.TextField("Additional Notes", blank=True)

    def code(self):
        return self.label + str(self.number)
    code.admin_order_field = models.functions.Concat('label', 'number')

    def __str__(self):
        return self.name

    def clean(self):
        if not str(self.label).isupper():
            raise ValidationError("Label must be a single uppercase letter")
    
    def save(self, *args, **kwargs):
        if self.number is None or self.label != Chemical.objects.get(pk=self.pk).label:
            query = Chemical.objects.filter(label__exact=self.label).order_by('-number')
            if query:
                self.number = query[0].number + 1
            else:
                self.number = 1
        super().save(*args, **kwargs)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['label', 'number'], name='unique_code')]
        verbose_name_plural = "          Chemicals"

class Primer(BaseModel):
    sequence = models.CharField(max_length=255)
    tm = models.FloatField()
    template = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    restriction_sites = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return str(self.pk)

    def clean(self):
        self.sequence = self.sequence.upper()
        if not re.fullmatch("[A,T,C,G,N,R,Y]+", self.sequence):
            raise ValidationError("Invalid DNA sequence")
    
    class Meta:
        verbose_name_plural = "       Primers"

class Plasmid(BaseModel):
    name = models.SlugField(max_length=255, unique=True)
    marker = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    primers = models.ManyToManyField(Primer, blank=True)
    files = GenericRelation(File)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "      Plasmids"

class Strain(BaseModel):
    name = models.SlugField(max_length=255, unique=True)
    species = models.CharField(max_length=255)
    genotype = models.CharField(max_length=255, blank=True)
    resistance = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    files = GenericRelation(File)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "     Strains"

class Stock(BaseModel):
    strain = models.ForeignKey(Strain, models.SET_NULL, null=True)
    plasmid = models.ForeignKey(Plasmid, models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name_plural = "    Stocks"

class Tag(models.Model):
    name = models.SlugField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Tags"

class Protocol(BaseModel):
    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)
    body = models.TextField()
    files = GenericRelation(File)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = " Protocols"

class Library(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "   Libraries"

def _plasmidmap_upload_location(instance, filename):
    return '%s/%s/%s' % (instance.library.name, instance.stock_id, filename)

class LibStock(models.Model):
    library = models.ForeignKey(Library, models.CASCADE)
    stock_id = models.CharField(max_length=255)

    plate = models.PositiveSmallIntegerField()
    letter = models.CharField(max_length=1)
    number = models.PositiveSmallIntegerField()

    species = models.CharField(max_length=255)
    gene_target = models.CharField(max_length=255, blank=True)
    plasmid_map = models.FileField(upload_to=_plasmidmap_upload_location, null=True, blank=True)
    forward_primer = models.ForeignKey(Primer, models.SET_NULL, null=True, blank=True)
    resistance = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def location(self):
        return "Plate %d, well %c%d" % (self.plate, self.letter, self.number)
    location.admin_order_field = 'plate'

    def __str__(self):
        return "%s %s" % (self.library.name, self.stock_id)

class Genome(BaseModel):
    title = models.CharField(max_length=255)
    body = models.TextField()
    files = GenericRelation(File)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "  Genomes"

class CrispriLibrary(models.Model):
    boxNo = models.CharField(max_length=255)
    plate = models.CharField(max_length=255)
    wellLetter = models.CharField(max_length=255)
    wellNo = models.CharField(max_length=255)
    locusTag = models.CharField(max_length=255)
    downStreamGene = models.CharField(max_length=255)
    forwardPrimer = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    resistance = models.CharField(max_length=255)
    essential = models.CharField(max_length=255)
    growthDefect = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Crispri Library"