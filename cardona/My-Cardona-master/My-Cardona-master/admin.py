import re

from django.contrib import admin
from django.contrib import messages
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.db import models
from django.utils.text import camel_case_to_spaces

from django.contrib.contenttypes.admin import GenericTabularInline

from .models import File, Bookmark, Chemical, Manufacturer, StorageLocation, Primer, Plasmid, Strain, Stock, Tag, Protocol, Library, LibStock, Genome
from .views import primer_add_multiple_view, create_library_view

class FileInline(GenericTabularInline):
    model = File
    extra = 0

class BaseModelAdmin(admin.ModelAdmin):
    # Admin site options
    actions = None # remove the "delete all selected" function
    list_display_links = None # no links directly to edit page

    # Variable to be set in child classes to specify detail view template
    detail_template = None

    # override to remove edit and delete buttons on foreignkey fields
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in form.base_fields:
            form.base_fields[field].widget.can_change_related = False
            form.base_fields[field].widget.can_delete_related = False
        return form

    # override to add detail view page
    def get_urls(self):
        urls = super().get_urls()
        view_urls = [path('<int:id>/view/', self.admin_site.admin_view(self.detail_view), name=self.model.__name__+"_view"),
                     path('<int:id>/add_bookmark/', self.admin_site.admin_view(self.add_bookmark_view), name=self.model.__name__+"_addbookmark"),
                     path('<int:id>/remove_bookmark/', self.admin_site.admin_view(self.remove_bookmark_view), name=self.model.__name__+"_removebookmark")]
        return view_urls + urls
    
    # view for object detail page
    def detail_view(self, request, id):
        if self.detail_template != None:
            object = self.get_object(request, id)
            is_bookmarked = False
            for bookmark in request.user.bookmark_set.all():
                if bookmark.content_object == object:
                    is_bookmarked = True
            context = dict(self.admin_site.each_context(request), object=object, object_type=camel_case_to_spaces(self.model.__name__), is_bookmarked=is_bookmarked)
            return TemplateResponse(request, self.detail_template, context)
        else:
            # Placeholder for if child class does not specify a template
            return HttpResponse("Detail template missing for this object type")
    
    def add_bookmark_view(self, request, id):
        new_bookmark = Bookmark(user=request.user, content_object=self.get_object(request, id))
        new_bookmark.save()
        messages.success(request, "Bookmark added")
        return HttpResponseRedirect("../view")

    def remove_bookmark_view(self, request, id):
        for bookmark in request.user.bookmark_set.all():
            if bookmark.content_object == self.get_object(request, id):
                bookmark.delete()
        messages.error(request, "Bookmark removed")
        return HttpResponseRedirect("../view")

class TrackCreatorAdmin(BaseModelAdmin):
    date_hierarchy = 'created'
    #readonly_fields = ['creator']
    exclude = ['creator']

    # override to automatically set object's creator
    def save_model(self, request, obj, form, change):
        if (not change):
            obj.creator = request.user
        super().save_model(request, obj, form, change)
        
class ManufacturerAdmin(BaseModelAdmin):
    actions = None
    search_fields = ['name']
    ordering = ['name']
    list_display = ['name_link']

    detail_template = "cardonalab/manufacturer_detail.html"

    def name_link(self, obj):
        return format_html("<a href=%s>%s</a>" % (reverse("admin:Manufacturer_view", args=[obj.id]), obj.name))
    name_link.short_description = 'Manufacturer'

class StorageLocationAdmin(BaseModelAdmin):
    actions = None
    search_fields = ['name']
    ordering = ['name']
    list_display = ['name_link']

    detail_template = "cardonalab/location_detail.html"

    def name_link(self, obj):
        return format_html("<a href=%s>%s</a>" % (reverse("admin:StorageLocation_view", args=[obj.id]), obj.name))
    name_link.short_description = 'Storage Location'

class ChemicalAdmin(TrackCreatorAdmin):
    list_display = ['code_link', 'name', 'location', 'in_stock']
    search_fields = ['name'] # can also search for code because of override method below
    list_filter = ['label', 'manufacturer', 'location', 'creator']
    autocomplete_fields = ['manufacturer', 'location']

    detail_template = "cardonalab/chemical_detail.html"

    def code_link(self, obj):
        return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Chemical_view", args=[obj.id]), obj.code()))
    code_link.short_description = 'code'
    code_link.admin_order_field = models.functions.Concat('label', 'number')

    # override to allow searching by code
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        codematch = re.fullmatch("([A-Z])([1-9]+)", search_term, re.I)
        if codematch is not None:
            queryset |= self.model.objects.filter(label=codematch.group(1).upper(), number=int(codematch.group(2)))
        return queryset, use_distinct

    class Media:
        js = ["cardonalab/chem_label_autoupdate.js"]

class PrimerAdmin(TrackCreatorAdmin):
    list_display = ['id_link', 'template', 'location', 'tm', 'restriction_sites', 'notes']
    list_filter = ['creator']
    search_fields = ['template', 'location', 'id', 'restriction_sites', 'notes']

    detail_template = "cardonalab/primer_detail.html"

    def id_link(self, obj):
        return format_html("<a href=%s><b>%d</b></a>" % (reverse("admin:Primer_view", args=[obj.id]), obj.id))
    id_link.short_description = 'id'
    id_link.admin_order_field = 'id'

    # override to include the "add multiple" page
    def get_urls(self):
        urls = super().get_urls()
        new_url = [path('add_multiple', self.admin_site.admin_view(primer_add_multiple_view), name='add_multiple')]
        return new_url + urls

class PlasmidAdmin(TrackCreatorAdmin):
    list_display = ['name_link', 'marker', 'notes']
    search_fields = ['name', 'marker', 'notes']
    list_filter = ['creator']
    filter_horizontal = ['primers']
    inlines = [FileInline]

    detail_template = "cardonalab/plasmid_detail.html"

    def name_link(self, obj):
        return format_html("<a href=%s>%s</a>" % (reverse("admin:Plasmid_view", args=[obj.id]), obj.name))
    name_link.short_description = 'name'
    name_link.admin_order_field = 'name'

class StrainAdmin(TrackCreatorAdmin):
    list_display = ['name_link', 'species', 'genotype', 'resistance', 'notes']
    search_fields = ['name', 'species', 'genotype', 'resistance', 'notes']
    inlines = [FileInline]

    detail_template = "cardonalab/strain_detail.html"

    def name_link(self, obj):
        return format_html("<a href=%s>%s</a>" % (reverse("admin:Strain_view", args=[obj.id]), obj.name))
    name_link.short_description = 'name'
    name_link.admin_order_field = 'name'

class StockAdmin(TrackCreatorAdmin):
    list_display = ['id_link', 'strain_link', 'plasmid_link', 'notes']
    search_fields = ['id', 'strain__name', 'plasmid__name', 'notes']
    autocomplete_fields = ['strain', 'plasmid']

    detail_template = "cardonalab/stock_detail.html"

    def id_link(self, obj):
        return format_html("<a href=%s><b>%d</b></a>" % (reverse("admin:Stock_view", args=[obj.id]), obj.id))
    id_link.short_description = 'id'
    id_link.admin_order_field = 'id'

    def strain_link(self, obj):
        if obj.strain:
            return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Strain_view", args=[obj.strain.id]), obj.strain))
        else:
            return ""
    strain_link.short_description = 'strain'
    strain_link.admin_order_field = 'strain'

    def plasmid_link(self, obj):
        if obj.plasmid:
            return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Plasmid_view", args=[obj.plasmid.id]), obj.plasmid))
        else:
            return ""
    plasmid_link.short_description = 'plasmid'
    plasmid_link.admin_order_field = 'plasmid'

class TagAdmin(BaseModelAdmin):
    actions = None
    list_display = ['tag_link']
    ordering = ['name']
    search_fields = ['name']

    detail_template = "cardonalab/tag_detail.html"

    def tag_link(self, obj):
        return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Tag_view", args=[obj.id]), obj.name))
    tag_link.short_description = 'tag'

class ProtocolAdmin(TrackCreatorAdmin):
    list_display = ['title_link', 'created', 'updated']
    search_fields = ['title', 'body']
    list_filter = ['tags', 'creator']
    filter_horizontal = ['tags']
    inlines = [FileInline]

    detail_template = "cardonalab/protocol_detail.html"

    def title_link(self, obj):
        return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Protocol_view", args=[obj.id]), obj.title))
    title_link.short_description = 'title'
    title_link.admin_order_field = 'title'

    class Media:
        js = ["tinymce/js/tinymce/tinymce.min.js", "cardonalab/protocol_text_editor.js"]

class LibraryAdmin(BaseModelAdmin):
    list_display = ['name_link', 'num_stocks']
    ordering = ['name']
    search_fields = ['name']

    def name_link(self, obj):
        return format_html("<a href=%s?library__id__exact=%d><b>%s</b></a>" % (reverse("admin:cardonalab_libstock_changelist"), obj.id, obj.name))
    name_link.short_description = 'name'
    name_link.admin_order_field = 'name'

    def num_stocks(self, obj):
        return obj.libstock_set.count()
    num_stocks.short_description = 'number of stocks'

    # override to include the "create from file" page
    def get_urls(self):
        urls = super().get_urls()
        new_url = [path('add/', self.admin_site.admin_view(create_library_view), name='create_library')]
        return new_url + urls

class LibStockAdmin(BaseModelAdmin):
    list_display = ['stock_id_link', 'location', 'species', 'gene_target', 'forward_primer_link', 'resistance', 'notes']
    list_filter = ['library']
    ordering = ['library', 'stock_id']

    detail_template = "cardonalab/libstock_detail.html"

    def stock_id_link(self, obj):
        return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:LibStock_view", args=[obj.id]), obj.stock_id))
    stock_id_link.short_description = 'stock id'
    stock_id_link.admin_order_field = 'stock_id'

    def forward_primer_link(self, obj):
        if obj.forward_primer:
            return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Primer_view", args=[obj.forward_primer.id]), obj.forward_primer))
        else:
            return ""
    forward_primer_link.short_description = 'forward primer'
    forward_primer_link.admin_order_field = 'forward_primer_id'

    # This override makes this model type not appear on the admin index page
    def get_model_perms(self, request):
        return {}
    
    # Override to only allow showing the list if it is filtering for a specific library
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        library_id = int(request.GET.get('library__id__exact', 0))
        if (library_id):
            extra_context['library'] = get_object_or_404(Library, pk=library_id)
            return super().changelist_view(request, extra_context=extra_context)
        else:
            return HttpResponseRedirect(reverse('admin:cardonalab_library_changelist'))

class GenomeAdmin(TrackCreatorAdmin):
    list_display = ['title_link', 'creator', 'created', 'updated']
    list_filter = ['creator']
    search_fields = ['title', 'body']
    inlines = [FileInline]

    detail_template = "cardonalab/genome_detail.html"

    def title_link(self, obj):
        return format_html("<a href=%s><b>%s</b></a>" % (reverse("admin:Genome_view", args=[obj.id]), obj.title))
    title_link.short_description = 'title'
    title_link.admin_order_field = 'title'

    class Media:
        js = ["tinymce/js/tinymce/tinymce.min.js", "cardonalab/protocol_text_editor.js"]

admin.site.register(Chemical, ChemicalAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(StorageLocation, StorageLocationAdmin)
admin.site.register(Primer, PrimerAdmin)
admin.site.register(Plasmid, PlasmidAdmin)
admin.site.register(Strain, StrainAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(LibStock, LibStockAdmin)
admin.site.register(Genome, GenomeAdmin)