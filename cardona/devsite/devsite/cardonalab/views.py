from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib import messages
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType

from .models import Primer, Library, LibStock

class PrimerAddMultipleForm(forms.Form):
    excel_file = forms.FileField(label="Upload file:")

def primer_add_multiple_view(request):
    if request.method == 'POST':
        form = PrimerAddMultipleForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                import xlrd
                sheet = xlrd.open_workbook(file_contents=excel_file.read()).sheet_by_index(0)

                if sheet.ncols == 6:
                    primers = []
                    errors = []
                    for i in range(1, sheet.nrows):
                        row = sheet.row_values(i)
                        try:
                            new_primer = Primer(creator=request.user,
                                                sequence=str(row[0]),
                                                tm=float(row[1]),
                                                template=str(row[2]),
                                                location=str(row[3]),
                                                restriction_sites=str(row[4]),
                                                notes=row[5])
                            new_primer.full_clean()
                            primers.append(new_primer)
                        except:
                            errors.append(i + 1)
                    
                    if not errors:
                        for new_primer in primers:
                            new_primer.save()
                            LogEntry.objects.log_action(
                                user_id=request.user.id,
                                content_type_id=ContentType.objects.get_for_model(new_primer).pk,
                                object_id=new_primer.id,
                                object_repr=str(new_primer),
                                action_flag=ADDITION,
                                change_message="Added via Excel file with primers %d - %d" % (primers[0].id, primers[0].id + len(primers) - 1)
                            )
                        messages.success(request, "Successfully created " + str(sheet.nrows-1) + " primers from file")
                    else:
                        messages.error(request, "File contains errors in the following row(s): " + str(errors))
                else:
                    messages.error(request, 'Incorrect number of columns in file "' + excel_file.name + '"')
            except xlrd.biffh.XLRDError:
                messages.error(request, 'Failed to read file "' + excel_file.name + '"')
            
            return HttpResponseRedirect('/cardonalab/primer')

    else:
        form = PrimerAddMultipleForm()
    
    return render(request, 'cardonalab/primer_add_multiple.html', {'form': form})

class CreateLibraryForm(forms.Form):
    library_name = forms.CharField(label="Library Name:")
    excel_file = forms.FileField(label="Upload file:")

def create_library_view(request):
    if request.method == 'POST':
        form = CreateLibraryForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                import xlrd
                sheet = xlrd.open_workbook(file_contents=excel_file.read()).sheet_by_index(0)

                if sheet.ncols == 9:
                    library = Library(name=form.cleaned_data['library_name'])
                    library.save()
                    stocks = []
                    errors = []
                    for i in range(1, sheet.nrows):
                        row = sheet.row_values(i)
                        try:
                            if row[6]:
                                primer = Primer.objects.get(pk=row[6])
                            else:
                                primer = None
                            try:
                                stock_id = int(row[0])
                            except:
                                stock_id = str(row[0])

                            new_stock = LibStock(
                                library=library,
                                stock_id=stock_id,
                                plate=row[1],
                                letter=row[2],
                                number=row[3],
                                species=row[4],
                                gene_target=row[5],
                                forward_primer=primer,
                                resistance=row[7],
                                notes=row[8])
                            new_stock.full_clean()
                            stocks.append(new_stock)
                        except:
                            errors.append(i + 1)
                    
                    if not errors:
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=ContentType.objects.get_for_model(library).pk,
                            object_id=library.id,
                            object_repr=str(library),
                            action_flag=ADDITION,
                            change_message="Added."
                        )
                        for new_stock in stocks:
                            new_stock.save()
                            LogEntry.objects.log_action(
                                user_id=request.user.id,
                                content_type_id=ContentType.objects.get_for_model(new_stock).pk,
                                object_id=new_stock.id,
                                object_repr=str(new_stock),
                                action_flag=ADDITION,
                                change_message="Added."
                            )
                        messages.success(request, "Successfully created library with " + str(sheet.nrows-1) + " stocks from file")
                    else:
                        library.delete()
                        messages.error(request, "File contains errors in the following row(s): " + str(errors))
                else:
                    messages.error(request, 'Incorrect number of columns in file "' + excel_file.name + '"')
            except xlrd.biffh.XLRDError:
                messages.error(request, 'Failed to read file "' + excel_file.name + '"')
            
            return HttpResponseRedirect('/cardonalab/library')

    else:
        form = CreateLibraryForm()
    
    return render(request, 'cardonalab/create_library.html', {'form': form})

def bookmarks_view(request):
    bookmarks = {'chemicals':[], 'manufacturers':[], 'locations':[], 'primers':[], 'plasmids':[], 'strains':[], 'stocks':[], 'libstocks':[], 'genomes':[], 'protocols':[], 'tags':[]}

    for bookmark in request.user.bookmark_set.all():
        if bookmark.content_type.model == 'chemical':
            bookmarks['chemicals'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'manufacturer':
            bookmarks['manufacturers'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'storagelocation':
            bookmarks['locations'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'primer':
            bookmarks['primers'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'plasmid':
            bookmarks['plasmids'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'strain':
            bookmarks['strains'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'stock':
            bookmarks['stocks'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'libstock':
            bookmarks['libstocks'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'genome':
            bookmarks['genomes'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'protocol':
            bookmarks['protocols'].append(bookmark.content_object)
        elif bookmark.content_type.model == 'tag':
            bookmarks['tags'].append(bookmark.content_object)

    context = dict(admin.site.each_context(request), bookmarks=bookmarks)
    return render(request, 'cardonalab/bookmarks.html', context)