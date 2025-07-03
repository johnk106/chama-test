from django.shortcuts import render
from Dashboard.models import *
from django.http import JsonResponse

from Goals.models import Goal
from notifications.utils import *
from authentication.models import *
# Create your views here.


def wallet_index(request):
    user_profile = Profile.objects.get(owner=request.user)

    user_active_chamas = Chamas.objects.filter(user_id=request.user, status='active')

    user_pending_chamas = Chamas.objects.filter(user_id=request.user, status='pending')
    p_to_p_wallet = Peer_to_Peer_Wallet.objects.get(user_id=user_profile.owner)
    saving_wallet = Saving_Wallet.objects.get(user_id=user_profile.owner)

    user_wallet = Wallet.objects.get(user_id=request.user)

    contribution_amount = contribution.objects.filter(user_id=request.user)
    Total_contribution = 0
    for item in contribution_amount:
        Total_contribution += item.amount

    user_notifications = UserNotificationHistory.objects.filter(user=request.user).order_by('-created_at')[:6]

    context = {'user_profile': user_profile, 'user_notifications': user_notifications,
               'user_active_chamas': user_active_chamas, 'user_pending_chamas': user_pending_chamas,
               'Total_contribution': Total_contribution, 'user_wallet': user_wallet, 'p_to_p_wallet': p_to_p_wallet,
               'saving_wallet': saving_wallet}
    return render(request, 'wallet.html', context)

def distribute_chama_bi_weekly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Bi-Weekly')

    business_logic=[]
    for aa in starting_wallet:
        business_logic.append(aa.name)

    unique_list=set(business_logic)


    for i in unique_list:

    #getting the chamaname just
        try:
            list_of_active_users=Chamas.objects.filter(name=i,Awarded='No').order_by('Award_turn')
            for a in list_of_active_users:
                print('line no 18',a)

            for item in list_of_active_users:
                print('list of users awarded with No order by asending',item.id ,item.user_id, item.name, item.Award_turn)
                x=Chamas.objects.get(id=int(item.id))
                Description='This transaction is reward chama contribution of '+x.name

                if not Wallet.objects.filter(user_id=item.user_id).exists():
                    purse=Wallet.objects.create(
                        chamas_id=x,
                        user_id=item.user_id,
                        available_for_withdraw=item.amount,
                        description=Description

                    )
                    purse.save()
                    x.Awarded='Yes'
                    x.save()

                    print('Wallet has been created ')
                else:
                    obj=Wallet.objects.get(user_id=item.user_id)
                    obj.chamas_id=x
                    obj.available_for_withdraw+=int(item.amount)
                    obj.description=Description
                    obj.save()
                    x.Awarded = 'Yes'
                    x.save()
                    phone_data_of_current_user = Profile.objects.get(owner=item.user_id)

                    text = 'Congratulation you have been rewareded by ChamaSpace for chama ' + str(
                        x.name) + ' with the amount of ' + str(
                        item.amount) + ' KS. Please login to portal and check details.Thanks'

                    # send_sms(phone_data_of_current_user.phone, 'Important Alert',text)
                    search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
                    send_notif(search_str, None, True, True, "Congratulation",
                               text,
                               None, False,
                               item.user_id)

                    break
        except Exception as e:
            print(e)
            return JsonResponse('No user is able to get chamabonus yet, wait few days.',safe=False)



    return JsonResponse('Chama bonus has been distrubuted successfully',safe=False)

def distribute_chama_weekly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Weekly')

    business_logic=[]
    for aa in starting_wallet:
        business_logic.append(aa.name)

    unique_list=set(business_logic)


    for i in unique_list:

    #getting the chamaname just
        try:
            list_of_active_users=Chamas.objects.filter(name=i,Awarded='No').order_by('Award_turn')
            for a in list_of_active_users:
                print('line no 18',a)

            for item in list_of_active_users:
                print('list of users awarded with No order by asending',item.id ,item.user_id, item.name, item.Award_turn)
                x=Chamas.objects.get(id=int(item.id))
                Description='This transaction is reward chama contribution of '+x.name

                if not Wallet.objects.filter(user_id=item.user_id).exists():
                    purse=Wallet.objects.create(
                        chamas_id=x,
                        user_id=item.user_id,
                        available_for_withdraw=item.amount,
                        description=Description

                    )
                    purse.save()
                    x.Awarded='Yes'
                    x.save()


                else:
                    obj=Wallet.objects.get(user_id=item.user_id)
                    obj.chamas_id=x
                    obj.available_for_withdraw+=int(item.amount)
                    obj.description=Description
                    obj.save()
                    x.Awarded = 'Yes'
                    x.save()
                    phone_data_of_current_user = Profile.objects.get(owner=item.user_id)

                    text = 'Congratulation you have been rewareded by ChamaSpace for chama ' + str(
                        x.name) + ' with the amount of ' + str(
                        item.amount) + ' KS. Please login to portal and check details.Thanks'

                    # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
                    search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
                    send_notif(search_str, None, True, True, "Congratulation",
                               text,
                               None, False,
                               item.user_id)
                    break



        except Exception as e:
            print(e)
            return JsonResponse('No user is able to get chamabonus yet, wait few days.',safe=False)



    return JsonResponse('Chama bonus has been distrubuted successfully',safe=False)

def distribute_chama_monthly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Monthly')

    business_logic=[]
    for aa in starting_wallet:
        business_logic.append(aa.name)

    unique_list=set(business_logic)


    for i in unique_list:

    #getting the chamaname just
        try:
            list_of_active_users=Chamas.objects.filter(name=i,Awarded='No').order_by('Award_turn')
            for a in list_of_active_users:
                print('line no 18',a)

            for item in list_of_active_users:
                print('list of users awarded with No order by asending',item.id ,item.user_id, item.name, item.Award_turn)
                x=Chamas.objects.get(id=int(item.id))
                Description='This transaction is reward chama contribution of '+x.name

                if not Wallet.objects.filter(user_id=item.user_id).exists():
                    purse=Wallet.objects.create(
                        chamas_id=x,
                        user_id=item.user_id,
                        available_for_withdraw=item.amount,
                        description=Description

                    )
                    purse.save()
                    x.Awarded='Yes'
                    x.save()


                else:
                    obj=Wallet.objects.get(user_id=item.user_id)
                    obj.chamas_id=x
                    obj.available_for_withdraw+=int(item.amount)
                    obj.description=Description
                    obj.save()
                    x.Awarded = 'Yes'
                    x.save()
                    phone_data_of_current_user = Profile.objects.get(owner=item.user_id)

                    text = 'Congratulation you have been rewareded by ChamaSpace for chama ' + str(
                        x.name) + ' with the amount of ' + str(
                        item.amount) + ' KS. Please login to portal and check details.Thanks'

                    # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
                    search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
                    send_notif(search_str, None, True, True, "Congratulation",
                               text,
                               None, False,
                               item.user_id)
                    break


        except Exception as e:
            print(e)
            return JsonResponse('No user is able to get chamabonus yet, wait few days.',safe=False)

    return JsonResponse('Chama bonus has been distrubuted successfully',safe=False)


def contribution_alert_biweekly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Bi-Weekly')


    for item in starting_wallet:
        if  datetime.date.today() == (item.contribution_date - relativedelta(days=3)):


            print('Line no 236 in contribution of bi weekly chama is:',item.contribution_date - relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is on date: '+ str(item.contribution_date) +'. Please pay your Bi-weekly contribution of ksh:' + str(item.amount) + 'early to avoid inconveniences. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)
        if  datetime.date.today() == item.contribution_date:
            item.contribution_date +=  relativedelta(days=14)
            item.save()
            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)



            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is today. Please pay your Bi-weekly contribution of ksh:' + str(
                item.amount) + 'before the end of day to avoid inconveniences. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)
        if  datetime.date.today() == (item.contribution_date + relativedelta(days=3)):


            print('Line no 270 in contribution of bi weekly chama is:',item.contribution_date + relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your are late in contribution of chama:  ' + str(
                item.name) +'. Please pay your Bi-weekly contribution of ksh:' + str(item.amount) + ' avoid an attractive fine. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)


    return JsonResponse('Contribution date reminder has been sent to all users.',safe=False)

def contribution_alert_weekly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Weekly')


    for item in starting_wallet:


        if  datetime.date.today() == (item.contribution_date - relativedelta(days=3)):


            print('Line no 300 in contribution of bi weekly chama is:',item.contribution_date - relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is on date: '+ str(item.contribution_date) +'. Please pay your weekly contribution of ksh:' + str(item.amount) + 'early to avoid inconveniences. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)
        if  datetime.date.today() == item.contribution_date:
            item.contribution_date +=  relativedelta(weeks=1)
            item.save()
            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)

            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is today. Please pay your weekly contribution of ksh:' + str(
                item.amount) + 'before the end of day to avoid inconveniences. Thanks.'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)


        if  datetime.date.today() == (item.contribution_date + relativedelta(days=3)):


            print('Line no 333 in contribution of bi weekly chama is:',item.contribution_date + relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your are late in contribution of chama:  ' + str(
                item.name) +'. Please pay your weekly contribution of ksh:' + str(item.amount) + ' avoid an attractive fine. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)




    return JsonResponse('Contribution date reminder has been sent to all users.',safe=False)
def contribution_alert_monthly(request):

    starting_wallet=Chamas.objects.filter(status='active',frequency_of_contribution='Monthly')


    for item in starting_wallet:


        if  datetime.date.today() == (item.contribution_date - relativedelta(days=3)):


            print('Line no 300 in contribution of bi Monthly chama is:',item.contribution_date - relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is on date: '+ str(item.contribution_date) +'. Please pay your monthly contribution of ksh:' + str(item.amount) + 'early to avoid inconveniences. Thanks.'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)
        if  datetime.date.today() == item.contribution_date:
            item.contribution_date +=  relativedelta(months=1)
            item.save()
            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)

            text = 'Dear customer! your contribution date for chama ' + str(
                item.name) + 'is today. Please pay your monthly contribution of ksh:' + str(
                item.amount) + 'before the end of day to avoid inconveniences. Thanks.'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)

        if  datetime.date.today() == (item.contribution_date + relativedelta(days=3)):


            print('Line no 333 in contribution of bi weekly chama is:',item.contribution_date + relativedelta(days=3))

            phone_data_of_current_user = Profile.objects.get(owner=item.user_id)


            text = 'Dear customer! your are late in contribution of chama:  ' + str(
                item.name) +'. Please pay your Monthly contribution of ksh:' + str(item.amount) + ' avoid an attractive fine. Thanks'

            # send_sms(phone_data_of_current_user.phone, 'Important Alert', text)
            search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
            send_notif(search_str, None, True, True, "Imprtant Alert",
                       text,
                       None, False,
                       item.user_id)




    return JsonResponse('Contribution date reminder has been sent to all users.',safe=False)




def end_chamas_life_completes(request):
    user_active_chamas = Chamas.objects.filter( status='active')


    for i in user_active_chamas:

        progress = (date.today() - i.start_date) / (i.end_date - i.start_date) * 100



        if progress >= 100:
            i.status = 'Life time expires'

            i.save()


    return JsonResponse('All chamas (length greater than 100)status changed to Life time expire ', safe=False)


def goal_contribution_alert(request):

    starting_wallet= Goal.objects.filter(is_active = 'Yes')


    for item in starting_wallet:
        print('Notification date is',item.notification_date)
        if item.notification_date is not None:



            if  datetime.date.today() == item.notification_date:
                print('Reminder freuency in notification alert:',item.reminder_frequency)
                if item.reminder_frequency == 'monthly':
                    item.notification_date +=  relativedelta(months=1)
                    item.save()
                if item.reminder_frequency == 'weekly':
                    item.notification_date +=  relativedelta(weeks=1)
                    item.save()
                if item.reminder_frequency == 'daily':
                    item.notification_date +=  relativedelta(days=1)
                    item.save()

                phone_data_of_current_user = Profile.objects.get(owner=item.user)
                print('Goal alert notification phone no to:',phone_data_of_current_user.phone)

                text = 'Dear customer! your deposit date for goal ' + str(
                    item.name) + 'is today. Please deposit your goal amount of ksh: ' + str(
                    item.amount_to_save_per_notification) + ' before the end of day to achieve goal on time. Thanks.'

                send_sms(phone_data_of_current_user.phone, 'Goal Alert', text)
                search_str = UserFcmTokens.objects.filter(user=item.user_id).order_by('-token')[:1]
                send_notif(search_str, None, True, True, "Goal Alert",
                           text,
                           None, False,
                           item.user)
                print('Goal notification has been sent to Mr. :',item.user.username)


    return JsonResponse('Goal deposit reminder has been sent to all users.',safe=False)