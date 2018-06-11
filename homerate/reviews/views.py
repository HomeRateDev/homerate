from urllib.parse import unquote

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import HouseForm, HouseReportForm, HouseDetailsForm
from .models import House
from .models import HouseReport
# Create your views here.

def house(request, id):
    if request.user.is_authenticated:	
        # Query database for house with correct id
        houses = House.objects.filter(id=id)

        # If no house found return a no house page
        # TODO make this it's own view and redirect instead
        if len(houses) == 0:
            return render(request, 'reviews/nohouse.html', {})

        house = houses[0]
        # Query database for reports about the house.
        reviews = HouseReport.objects.filter(house_filed=house).order_by('-moved_out_date')
        for report in reviews:
            report.get_general_rating()
        rating = house.star_rating()

        # Construct a split-up version of the address
        address_components = house.split_address()

        # return house view page with house and list of reports
        return render(
            request, 'reviews/house.html', {
                'house': house,
                'reviews': reviews,
                'rating': rating,
                'address_components': address_components
            }
        )
    else:
        return render(request, 'reviews/login_to_view_reports.html')
        
        

@login_required
def new_report(request, id):
    # Get relevant house
    houses = House.objects.filter(id=id)

    # Check house exists
    if len(houses) == 0:
        return render(request, 'reviews/nohouse.html', {})
    house = houses[0]

    # Check a POST request has been received
    if request.method == "POST":
        house_details_form = HouseDetailsForm(request.POST, instance=house)
        review_form = HouseReportForm(request.POST, request.FILES)

        # Ensure both forms are valid
        if house_details_form.is_valid() and review_form.is_valid():

            # Prepare to save review, but don't commit to database yet
            report = review_form.save(commit=False)

            # Insert foreign key from House model
            report.house_filed = house

            # Save house details
            house_details_form.save()

            report.author = request.user

            # Commit review to database
            report.save()

            return redirect('house', id=house.id)
        else:
            print("Form Error")
            print(review_form.errors)
            print(house_details_form.errors)

    house_details_form = HouseDetailsForm(instance=house)
    review_form = HouseReportForm()

    return render(request, 'reviews/newreport.html', {
                      'house_details_form': house_details_form,
                      'new_report_form': review_form,
                      'house': house,
                  })


@login_required
def edit_report(request, id):
    report = get_object_or_404(HouseReport, pk=id)
    house = report.house_filed

    if request.method == "POST":
        house_details_form = HouseDetailsForm(request.POST, instance=house)
        review_form = HouseReportForm(request.POST, request.FILES, instance=report)

        # Ensure both forms are valid
        if house_details_form.is_valid() and review_form.is_valid():

            # Prepare to save review, but don't commit to database yet
            report = review_form.save(commit=False)

            # Insert foreign key from House model
            report.house_filed = house

            # Save house details
            house_details_form.save()

            report.author = request.user

            # Commit review to database
            report.save()

            return redirect('house', id=house.id)
        else:
            print("Form Error")
            print(review_form.errors)
    else:
        house_details_form = HouseDetailsForm(instance=house)
        review_form = HouseReportForm(instance=report)

        return render(request, 'reviews/newreport.html', {
            'house_details_form': house_details_form,
            'new_report_form': review_form,
            'house': house,
        })

@login_required
def delete_report(request, id):
    report = get_object_or_404(HouseReport, pk=id)
    house = report.house_filed
    report.delete()
    return redirect('house', id=house.id)


def check_house(request, encoded_addr):
    # Decode the address
    address_str = unquote(encoded_addr)

    # Query the database to check if the house already exists
    query = House.objects.filter(address=address_str)

    if query.count() > 0:
        # The house exists, redirect to it
        return redirect('house', id=query.first().id)
    else:
        # The house doesn't exist, create a new house
        new_house_entry = House(address=str(address_str))
        new_house_entry.save()
        return redirect('house', id=new_house_entry.id)
