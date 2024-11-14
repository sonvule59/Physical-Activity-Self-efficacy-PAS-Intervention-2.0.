import datetime as dt
import logging
import operator
import tempfile
import pandas as pd

from django.contrib.auth.models import AbstractUser
from django.db import models
# from django_quill.fields import QuillField
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from multiselectfield import MultiSelectField
# from phonenumber_field.modelfields import PhoneNumberField

# from intervention.helpers import get_unique_slug, parse_raw_sql

# logger = logging.getLogger(__name__)


# class User(AbstractUser, models.Model):
#     email = models.EmailField(unique = True)
#     email_confirmed = models.BooleanField(default=False)
#     activated_at = models.DateTimeField(null=True, blank=True)
#     birthday = models.DateField(null=True, blank=True)
#     phone_number = PhoneNumberField(blank=True, region="US")

#     class Meta:
#         verbose_name = _("user")
#         verbose_name_plural = _("users")
#         constraints = [
#             models.UniqueConstraint(
#                 models.functions.Lower("email"),
#                 name="user_email_case_uniqueness",
#             ),
#         ]


#     def age(self):
#         return int((dt.date.today() - self.birthday).days / 365.25) if self.birthday else 0

# ##################
# ##################
# ##################

# class InterventionQuerySet(models.QuerySet):
#     # Fetch data for CSV Report
#     @parse_raw_sql
#     def get_user_responses(self, intervention_id):
#         """ 
#         This method returns the query set that will be used the for the 
#         CSV report.
        
#         This method uses f-strings for intervals in order to
#         provide the test mode functionality.
#         """
#         sql = """ 
#         WITH questions AS (
#             SELECT
#                 question.id,
#                 survey.id AS survey,
#                 question.title
#             FROM intervention_surveyquestion question
#                 INNER JOIN intervention_interventionsurvey survey ON question.survey_assignment_id = survey.id
#                 INNER JOIN intervention_intervention inter ON inter.id = survey.intervention_id
#                 WHERE inter.id = %(intervention_id)s
#             ORDER BY question.id DESC
#             ),
#         answers AS (
#             SELECT
#                 question.id AS question_id,
#                 usr.id AS user_id,
#                 usr.email AS email,
#                 grup.group_assignment AS grupo,
#                 usr.username AS username,
#                 answer.id AS answer_id,
#                 answer.answer AS answer
#             FROM intervention_user usr
#                 JOIN intervention_interventionmembership grup ON usr.id = grup.user_id
#                 LEFT JOIN intervention_surveyresponses res ON res.responder_id = usr.id
#                 LEFT JOIN intervention_surveyresponses_response resres ON resres.surveyresponses_id = res.id
#                 LEFT JOIN intervention_surveyanswer AS answer ON answer.id = resres.surveyanswer_id
#                 LEFT JOIN intervention_surveyquestion AS question ON question.id = answer.answer_to_id
#             )
#         SELECT
#         DISTINCT questions.id AS question_id,
#         answers.answer_id AS answer_id,
#         answers.user_id AS user_id,
#         questions.survey AS survey,
#         CONCAT(questions.id, ' ', questions.title) AS question,
#         answers.grupo AS grupo,
#         answers.username AS username,
#         answers.email AS email,
#         answers.answer AS answer
#         FROM questions
#         FULL OUTER JOIN answers ON questions.id = answers.question_id
#         ORDER BY answers.email ASC;
#         """
#         return sql, { "intervention_id": intervention_id }

#     # Create the dataframes with panda and generate the CSV file separated by ;
#     def process_user_responses_for_csv(self, intervention_id):
#         qs = self.get_user_responses(intervention_id=intervention_id)
#         dtf = pd.DataFrame(qs)
#         main_data = dtf.pivot_table(index=['user_id'], 
#                                     columns='question', 
#                                     values='answer', 
#                                     aggfunc='sum', 
#                                     dropna=False)
#         user_qs = User.objects.filter(
#         interventionmembership__intervention=intervention_id
#         )
#         users = []
#         challenge = Challenge.objects.get(
#             title='Introductory Challenge 4: Self-efficacy to Engage')
#         prompts = Prompt.objects.filter(challenge_assignment=challenge)
#         for user in user_qs:
#             user_data = {
#                 "id": user.id,
#                 "email": user.email,
#                 "username": user.username,
#                 "age": user.age(),
#                 "challenges_completed": self.get_challenges_completed(user),
               
#             }
#             user_data.update(self.get_introductory_challenge_4(user, challenge, prompts))
#             users.append(user_data)
#         users_dtf=pd.DataFrame(users).set_index("id")
#         group=pd.DataFrame(InterventionMembership.objects.filter(intervention=intervention_id)
#                            .values(
#                                'user', 
#                                'height_feet', 
#                                'height_inches',
#                                'created_at', 
#                                'weight', 
#                                'group_assignment', 
#                                'has_device',
#                                'no_compete',
#                                'has_intervention_access', 
#                                'physical_activity_monitor', 
#                                'will_respond', 
#                                'consent', 
#                                'activated_at',
#                                'is_pre_monitor_answered', 
#                                'is_post_monitor_answered')).set_index("user")
#         usr_info=pd.concat([users_dtf, group], axis=1)
#         data_frame_2= pd.concat([usr_info, main_data], axis=1)
#          # Create a temporary CSV file
#         with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
#             csv_path = temp_file.name
#             data_frame_2.to_csv(csv_path, sep=',')
#         return csv_path
    
#     def get_challenges_completed(self, user: User):
#         '''Returns the number of challenges completed for the given user'''
#         intervention_set = Intervention.objects.all()
#         progress_counter = 0
#         for i in intervention_set.iterator():
#             for co in i.component_set.all():
#                 for c in co.challenge_set.all():
#                     check_progress = Progress.objects.filter(user=user,challenge=c)
#                     if check_progress:
#                         progress_counter += 1
#         return progress_counter
    
#     def get_introductory_challenge_4(self, user: User, challenge, prompts):
#         prompts = list(prompts)
#         response_dict = {f"introductory_challenge_4_{i}": None for i, _ in enumerate(prompts)}
#         response = Responses.objects.filter(responder=user, response_to=challenge).last()
    
#         # Check if a response exists
#         if response:
#             answers = Answer.objects.filter(response=response)
            
#             # Iterate through each answer
#             for answer in answers:
#                 prompt_index = prompts.index(answer.answer_to)
#                 response_dict[f"introductory_challenge_4_{prompt_index}"] = answer.answer
        
#         return response_dict
            
    
# GROUP_CHOICES = (
#     ("a", "A"),
#     ("b", "B"),
# )

# class Intervention(models.Model):
#     class InterventionSurveyIntervals(models.TextChoices):
#         YEARS = "years"
#         MONTHS = "months"
#         WEEKS = "weeks"
#         DAYS = "days"
#         MINUTES = "mins"
    
#         def get_dt_kwargs(self, value_to_map: int) -> dict:
#             """
#             Given the differences between interval unit names in the SQL and
#             the ones used by `dt.timedelta`, this method returns a
#             dictionary to be used as kwargs for `dt.timedelta`

#             Returns:
#                 dict: Dictionary
#             """
#             mapping = {
#                 "years": "years",
#                 "months": "months",
#                 "weeks": "weeks",
#                 "days": "days",
#                 "mins": "minutes"
#             }
#             return {mapping[self.value]: value_to_map}
    
#         def dt_mins(self, dt_instance: dt.datetime) -> dt.datetime:
#             return dt_instance.replace(second=0, microsecond=0)

#         def dt_days(self, dt_instance: dt.datetime) -> dt.date:
#             return dt_instance.date()
        
#         def dt_weeks(self, dt_instance: dt.datetime) -> dt.date:
#             return dt_instance.date() - dt.timedelta(days=dt_instance.weekday())
        
#         def dt_months(self, dt_instance: dt.datetime)-> dt.datetime:
#             return dt_instance.replace(day=1)

#         def dt_years(self, dt_instance: dt.datetime) -> dt.datetime:
#             return dt_instance.replace(month=1, day=1)
        
#         def dt(self, dt_instance: dt.datetime) -> dt.datetime | dt.date:
#             return getattr(self, f"dt_{self.value}")(dt_instance)

#     title = models.CharField(max_length=128)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)
#     interval = models.CharField(
#         'Intervention Survey Interval',
#         choices=InterventionSurveyIntervals.choices,
#         default=InterventionSurveyIntervals.DAYS,
#         max_length=20
#     )
#     duration = models.PositiveIntegerField(default=1, blank=False, null=False, verbose_name="Intervention Duration (days)")
#     registration_code = models.CharField(max_length=12, blank=True)
#     groups = MultiSelectField('Membership Groups', choices=GROUP_CHOICES, default=['a', 'b'], max_length=20)
#     subtitle = models.CharField(max_length=128)
#     description = QuillField(blank=True)
#     consent_message = QuillField(blank=True)
#     # reminder message email before post intervention survey starts
#     reminder_message = QuillField(blank=True)
#     reminder_subject = models.CharField(max_length=80, blank=True, null=True)
#     # thankyou message email after post intervention survey
#     thank_you_message = QuillField(blank=True)
#     thankyou_email_subject = models.CharField(max_length=80, blank=True, null=True)
#     send_reminders = models.BooleanField(default=True)
#     is_active = models.BooleanField(default=False)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(default=timezone.now)
#     members_number = models.PositiveIntegerField(default=1, blank=False, null=False)

#     objects = InterventionQuerySet.as_manager()
    
#     def __str__(self):
#         return self.title

#     @property
#     def interval_enum(self) -> InterventionSurveyIntervals:
#         return Intervention.InterventionSurveyIntervals(self.interval)

#     def get_absolute_url(self):
#         return reverse('intervention:intervention_detail', args=[str(self.slug)])

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = get_unique_slug(self, 'title', 'slug')
#         super().save(*args, **kwargs)

# ##################
# ##################
# ##################

# class InterventionSurveySet(models.QuerySet):

#     def get_intervention_map(self, user, intervention):
#         """
#         This is the main method to obtain the intervention map
#         for a given user and intervention.
        
#         This method uses f-strings for intervals in order to
#         provide the test mode functionality.

#         This is less than ideal, however these interpolations are done
#         on the database query schema, so there is no risk of SQL injection.
        
#         https://stackoverflow.com/a/46669121
#         """
#         sql = f"""
#             WITH intervals AS (
#                 SELECT
#                     res.id,
#                     res.created_at AS res_created,
#                     CASE
#                         WHEN insur.survey_type <> 'monitor'
#                         THEN make_interval({intervention.interval} =>insur.survey_duration)
#                         ELSE make_interval({intervention.interval} =>insur.grace_period)
#                     END
#                     AS survey_duration,
#                     insur.assingment_type AS ass_type,
#                     (
#                         CASE
#                             WHEN
#                                 insur.independent_survey = TRUE
#                             THEN
#                                 mem.created_at + (make_interval({intervention.interval} =>insur.launch_at) * 7)
#                             ELSE res.created_at
#                         END
#                     ) +
#                     CASE
#                         WHEN
#                             insur.survey_type = 'monitor' AND NOT insur.independent_survey = TRUE
#                         THEN
#                             make_interval({intervention.interval} =>insur.grace_period)
#                         ELSE make_interval({intervention.interval} =>insur.survey_duration)
#                     END
#                     AS survey_exp
#                 FROM intervention_SurveyResponses res
#                 INNER JOIN intervention_interventionsurvey insur ON insur.id = res.response_to_id
#                 INNER JOIN intervention_user usr ON res.responder_id = usr.id
#                 INNER JOIN intervention_interventionmembership mem ON mem.user_id = usr.id
#                 ORDER BY ass_type, insur.position
#             ),

#             time_line AS (
#                 SELECT
#                     res.id,
#                     inter.id AS inter_id,
#                     usr.username,
#                     insur.id AS insur_id,
#                     insur.position AS survey_position,
#                     res.created_at AS res_created,
#                     intervals.survey_duration,
#                     mem.group_assignment AS mem_group_assignment,
#                     mem.created_at AS mem_created,
#                     intervals.survey_exp AS survey_exp,
#                     insur.survey_type,
#                     intervals.ass_type
#                 FROM intervention_SurveyResponses res
#                 INNER JOIN intervention_interventionsurvey insur ON insur.id = res.response_to_id
#                 INNER JOIN intervention_user usr ON res.responder_id = usr.id
#                 INNER JOIN intervention_intervention inter ON insur.intervention_id = inter.id
#                 INNER JOIN intervention_interventionmembership mem ON mem.user_id = usr.id
#                 INNER JOIN intervals ON intervals.id = res.id
#                 WHERE usr.username = %(username)s
#                 ORDER BY survey_position
#             )

#             SELECT
#                 insur.id,
#                 CASE
#                     WHEN insur.assingment_type = 'pre_intervention' THEN 1
#                     WHEN insur.assingment_type = 'post_intervention' THEN 3
#                     ELSE 2
#                 END
#                 AS insur_assingment_type_num,
#                 insur.assingment_type AS assignment_type,
#                 insur.position AS insur_position,
#                 insur.survey_type AS insur_survey_type,
#                 inter.id AS inter_id,
#                 tl.id AS res_id,
#                 tl.username AS username,
#                 COALESCE(
#                     tl.mem_group_assignment,
#                     LAG(
#                         mem_group_assignment, 1
#                     ) OVER(
#                         PARTITION BY inter.id
#                         ORDER BY insur.id
#                     )
#                 ) AS mem_group_assignment,
#                 CASE
#                     WHEN tl.res_created IS NULL THEN 'Estimated'
#                     ELSE 'Actual'
#                 END
#                 AS res_start_type,
#                 CASE
#                     WHEN tl.survey_exp IS NULL THEN 'Estimated'
#                     ELSE 'Actual'
#                 END
#                 AS res_survey_exp_type,
#                 tl.res_created AS answered_at,
#                 COALESCE(
#                     tl.res_created,
#                     CASE
#                         WHEN
#                             insur.independent_survey = true
#                         THEN
#                             FIRST_VALUE(
#                                 tl.mem_created
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + (make_interval({intervention.interval} =>insur.launch_at) * 7)
#                         WHEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) IS NOT NULL
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             +
#                             CASE
#                                 WHEN
#                                     LAG(
#                                         insur.assingment_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) <> insur.assingment_type
#                                     AND
#                                     LAG(
#                                         insur.survey_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) = 'monitor'
#                                 THEN
#                                     make_interval(
#                                         {intervention.interval} =>
#                                         LAG(
#                                             insur.survey_duration, 1
#                                         ) OVER(
#                                             PARTITION BY inter.id
#                                             ORDER BY insur.id
#                                         )
#                                     )
#                                     +
#                                     make_interval({intervention.interval} =>inter.duration)
#                                 WHEN
#                                     LAG(
#                                         insur.assingment_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) <> insur.assingment_type
#                                     AND
#                                     LAG(
#                                         insur.survey_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) <> 'monitor'
#                                 THEN
#                                     make_interval({intervention.interval} =>inter.duration)
#                                 WHEN
#                                     LAG(
#                                         insur.assingment_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) = insur.assingment_type
#                                     AND
#                                     LAG(
#                                         insur.survey_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) = 'monitor'
#                                 THEN
#                                     make_interval(
#                                         {intervention.interval} =>
#                                         LAG(
#                                             insur.survey_duration, 1
#                                         ) OVER(
#                                             PARTITION BY inter.id
#                                             ORDER BY insur.id
#                                         )
#                                     )
#                                     +
#                                     make_interval({intervention.interval} =>0)
#                                 WHEN
#                                     LAG(
#                                         insur.assingment_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) = insur.assingment_type
#                                     AND
#                                     LAG(
#                                         insur.survey_type, 1
#                                     ) OVER(
#                                         PARTITION BY inter.id
#                                         ORDER BY insur.id
#                                     ) <> 'monitor'
#                                 THEN
#                                     make_interval({intervention.interval} =>0)
#                             END
#                         ELSE
#                             FIRST_VALUE(
#                                 tl.mem_created
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                     END
#                 ) AS res_expected_start,
#                 COALESCE(
#                     CASE
#                         WHEN    
#                             insur.survey_type = 'monitor'
#                         THEN
#                             tl.res_created
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                         ELSE
#                             tl.res_created
#                     END,
#                     CASE
#                         WHEN
#                             insur.independent_survey = true
#                         THEN
#                             FIRST_VALUE(
#                                 tl.mem_created
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + (make_interval({intervention.interval} =>insur.launch_at) * 7)
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                         WHEN
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) <> insur.assingment_type
#                             AND
#                             LAG(
#                                 insur.survey_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = 'monitor'
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                             + make_interval({intervention.interval} =>inter.duration)
#                             + make_interval(
#                                 {intervention.interval} =>
#                                 LAG(
#                                     insur.survey_duration, 1
#                                 ) OVER(
#                                     PARTITION BY inter.id
#                                     ORDER BY insur.id
#                                 )
#                             )
#                         WHEN
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) <> insur.assingment_type
#                             AND
#                             LAG(
#                                 insur.survey_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) <> 'monitor'
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                             + make_interval({intervention.interval} =>inter.duration)
#                         WHEN
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = insur.assingment_type
#                             AND
#                             LAG(
#                                 insur.survey_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = 'monitor'
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + make_interval(
#                                 {intervention.interval} =>
#                                 LAG(
#                                     insur.survey_duration, 1
#                                 ) OVER(
#                                     PARTITION BY inter.id
#                                     ORDER BY insur.id
#                                 )
#                             )
#                             +
#                             CASE
#                             WHEN
#                                 insur.survey_type = 'monitor' AND NOT insur.independent_survey = TRUE
#                             THEN
#                                 make_interval({intervention.interval} =>insur.grace_period)
#                                 + make_interval({intervention.interval} =>insur.survey_duration)
#                             ELSE
#                                 make_interval({intervention.interval} =>insur.survey_duration)
#                             END
#                         WHEN
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = insur.assingment_type
#                             AND
#                             insur.survey_type = 'monitor'
#                         THEN
#                             CASE
#                             WHEN
#                                 tl.res_created IS NULL
#                             THEN
#                                 LAG(
#                                     tl.res_created, 1
#                                 ) OVER(
#                                     PARTITION BY inter.id
#                                     ORDER BY insur.id
#                                 )
#                                 + make_interval({intervention.interval} =>insur.grace_period)
#                             ELSE
#                                 LAG(
#                                     tl.res_created, 1
#                                 ) OVER(
#                                     PARTITION BY inter.id
#                                     ORDER BY insur.id
#                                 )
#                                 + make_interval({intervention.interval} =>insur.grace_period)
#                                 + make_interval({intervention.interval} =>insur.survey_duration)
#                             END
#                         WHEN 
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = insur.assingment_type
#                             AND
#                             insur.survey_type <> 'monitor'
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                         WHEN
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) <> insur.assingment_type
#                             AND
#                             insur.survey_type = 'monitor'
#                         THEN
#                             LAG(
#                                 tl.res_created, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             + make_interval({intervention.interval} =>insur.grace_period)
#                             + make_interval({intervention.interval} =>insur.survey_duration)
#                             + make_interval({intervention.interval} =>inter.duration)
#                         ELSE
#                             FIRST_VALUE(
#                                 tl.mem_created
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             )
#                             +
#                             CASE
#                             WHEN
#                                 insur.survey_type = 'monitor' AND NOT insur.independent_survey = TRUE
#                             THEN
#                                 make_interval({intervention.interval} =>insur.grace_period)
#                             ELSE
#                                 make_interval({intervention.interval} =>insur.survey_duration)
#                             END
#                     END
#                 )
#                 AS res_survey_exp,
#                 (
#                     SELECT
#                         tl.res_created
#                     FROM time_line tl
#                     WHERE
#                         tl.ass_type = 'pre_intervention'
#                         AND tl.inter_id = inter.id
#                     ORDER BY
#                         tl.survey_position
#                     DESC
#                     LIMIT 1
#                 ) AS int_expected_start,
#                 (
#                     SELECT
#                         tl.res_created
#                     FROM time_line tl
#                     WHERE tl.ass_type = 'pre_intervention'
#                     ORDER BY
#                         tl.survey_position
#                     DESC
#                     LIMIT 1
#                 ) + make_interval({intervention.interval} =>inter.duration)
#                 AS int_expiration,
#                 (
#                     CASE
#                         WHEN
#                             LAG(
#                                 insur.survey_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = 'monitor'
#                             AND
#                             LAG(
#                                 insur.assingment_type, 1
#                             ) OVER(
#                                 PARTITION BY inter.id
#                                 ORDER BY insur.id
#                             ) = 'post_intervention'
#                         THEN 
#                             True
#                         ELSE
#                             False
#                     END
#                 ) AS is_previous_post_monitor
#             FROM intervention_interventionsurvey insur
#             INNER JOIN intervention_intervention inter ON insur.intervention_id = inter.id
#             LEFT JOIN time_line tl ON tl.insur_id = insur.id
#             WHERE inter.id = %(intervention_id)s
#             ORDER BY
#                 insur_assingment_type_num,
#                 insur.position
#         """
#         return self.raw(
#             sql,
#             params={
#                 "username": user.username,
#                 "intervention_id": intervention.pk
#             }
#         )

#     def get_empty_intervention_surveys(self, user, intervention):
#         qs = self.get_intervention_map(user, intervention)
#         surveys: list[InterventionSurvey] = [x for x in qs if x.is_redirect_candidate()]
#         try:
#             survey: InterventionSurvey = surveys[0]
#         except IndexError:
#             survey = None
#         try:
#             following: InterventionSurvey = surveys[1]
#         except IndexError:
#             following = None
#         if survey is None:
#             return (survey, following, surveys)
#         try:
#             insur_count = survey.intervention.interventionsurvey_set.all().count()
#             if survey.res_expected_start is None and insur_count == len(surveys):
#                 # user has not responded any surveys yet
#                 mem: InterventionMembership = user.interventionmembership_set.get(intervention=intervention)
#                 survey.res_expected_start = mem.created_at
#                 survey.username = user.username
#                 survey.mem_group_assignment = mem.group_assignment
#                 survey.res_survey_exp = survey.res_expected_start + dt.timedelta(
#                     **survey.intervention.interval_enum.get_dt_kwargs(survey.survey_duration)
#                 )
#             elif survey.res_expected_start is None:
#                 previous = [x for x in qs if not x.is_redirect_candidate()][-1]
#                 try:
#                     survey = qs[list(qs).index(previous) +1]
#                 except IndexError:
#                     survey = None
#                     following = None
#                 else:
#                     survey = survey.calculate_expected_dates(previous, user)
#                     try:
#                         following = qs[list(qs).index(survey) +1]
#                     except IndexError:
#                         following = None
#         except InterventionMembership.DoesNotExist:
#             survey = False
#             following = False
#         return (survey, following, surveys)

#     def get_answered_intervention_surveys(self, user, intervention):
#         qs = self.get_intervention_map(user, intervention)
#         surveys: list[InterventionSurvey] = [x for x in qs if x.answered_at]
#         return surveys

# TYPE_CHOICES = (
#     ("standard", "Standard"),
#     ("monitor", "Monitor"),
# )

# class InterventionSurvey(models.Model):

#     class AssignmentType(models.TextChoices):
#         STANDARD = 'standard', 'Standard'
#         PRE_INTERVENTION = 'pre_intervention', 'Pre-Intervention'
#         POST_INTERVENTION = 'post_intervention', 'Post-Intervention'

#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length=128)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)
#     grace_period = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Grace Period (days)")
#     survey_duration = models.PositiveIntegerField(default=1, blank=False, null=False, verbose_name="Survey Duration (days)")
#     independent_survey = models.BooleanField(default=False)
#     launch_at = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Independent Launch at (weeks)")
#     launch_subject = models.CharField(max_length=80, null=True, blank=True)
#     launch_subject_addendum_a = models.CharField(max_length=80, null=True, blank=True)
#     launch_subject_addendum_b = models.CharField(max_length=80, null=True, blank=True)
#     launch_message = QuillField(blank=True)
#     launch_message_addendum_a = QuillField(blank=True, verbose_name="Launch Addendum (Group A: Intervention)")
#     launch_message_addendum_b = QuillField(blank=True, verbose_name="Launch Addendum (Group B: Usual Care)")
#     survey_type = models.CharField('Survey Type', choices=TYPE_CHOICES, default='standard', max_length=20)
#     monitor_code = models.CharField(max_length=12, blank=True)
#     monitor_reminder_subject = models.CharField(max_length=80, null=True, blank=True)
#     monitor_reminder_message = QuillField(blank=True)
#     monitor_expired_subject = models.CharField(max_length=80, null=True, blank=True)
#     monitor_expired_subject_addendum_a = models.CharField(max_length=80, null=True, blank=True)
#     monitor_expired_subject_addendum_b = models.CharField(max_length=80, null=True, blank=True)
#     monitor_expired_message = QuillField(blank=True)
#     monitor_expired_message_addendum_a = QuillField(blank=True, verbose_name="Monitor Expired Addendum (Group A: Intervention)")
#     monitor_expired_message_addendum_b = QuillField(blank=True, verbose_name="Monitor Expired Addendum (Group B: Usual Care)")
#     send_reminders = models.BooleanField(default=True)
#     intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
#     assingment_type = models.CharField(max_length=17, choices=AssignmentType.choices, default=AssignmentType.STANDARD, verbose_name="Assignment Type")
#     description = QuillField(blank=True)
#     thank_you_subject = models.CharField(max_length=80, null=True, blank=True)
#     thank_you_subject_addendum_a = models.CharField(max_length=80, null=True, blank=True)
#     thank_you_subject_addendum_b = models.CharField(max_length=80, null=True, blank=True)
#     thank_you_message = QuillField(blank=True)
#     thank_you_message_addendum_a = QuillField(blank=True, verbose_name="Thank You Addendum (Group A: Intervention)")
#     thank_you_message_addendum_b = QuillField(blank=True, verbose_name="Thank You Addendum (Group B: Usual Care)")
#     reminder_subject = models.CharField(max_length=80, null=True, blank=True)
#     reminder_message = QuillField(blank=True)
#     expired_subject = models.CharField(max_length=80, null=True, blank=True)
#     expired_subject_addendum_a = models.CharField(max_length=80, null=True, blank=True)
#     expired_subject_addendum_b = models.CharField(max_length=80, null=True, blank=True)
#     expired_message = QuillField(blank=True)
#     expired_message_addendum_a = QuillField(blank=True, verbose_name="Expired Addendum (Group A: Intervention)")
#     expired_message_addendum_b = QuillField(blank=True, verbose_name="Expired Addendum (Group B: Usual Care)")
#     pre_expiration_reminder = models.IntegerField(default=1) 

#     objects = InterventionSurveySet.as_manager()

#     def __str__(self):
#         return self.title

#     @property
#     def assingment_type_enum(self) -> AssignmentType:
#         return InterventionSurvey.AssignmentType(self.assingment_type)

#     def get_survey_by_position(self, qs, position):
#         try:
#             return [x for x in qs if x.position == position][0]
#         except IndexError:
#             return None

#     def calculate_expected_dates_recursively(self, usr, empty_surveys):
#         following = self.get_survey_by_position(empty_surveys, self.position+1)
#         if self.position == 0 or (hasattr(self,'answered_at') and self.answered_at is not None):
#             return self, following
#         else:
#             prev = self.get_survey_by_position(empty_surveys, self.position-1)
#             if prev is not None:
#                 prev, _ = prev.calculate_expected_dates_recursively(usr, empty_surveys)
#                 self.calculate_expected_dates(prev, usr)
#             return self, following

#     def inside_intervention(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         if not self.int_expected_start or not self.int_expiration:
#             return None
#         return self.intervention.interval_enum.dt(now) >= self.intervention.interval_enum.dt(self.int_expected_start) and \
#             self.intervention.interval_enum.dt(now) <= self.intervention.interval_enum.dt(self.int_expiration)
    
#     def inside_intervention_empty_surveys(self, following: "InterventionSurvey"):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         inside_intervention = self.inside_intervention()
#         if inside_intervention is None:
#             following_is_intervention = following.assingment_type != self.assingment_type
#             is_invalid = not self.validate_expiration()
#             if is_invalid and following_is_intervention:
#                 # lets try to guess intervention intervals
#                 self.int_expected_start = self.res_survey_exp
#                 self.int_expiration = self.res_survey_exp + dt.timedelta(
#                     **self.intervention.interval_enum.get_dt_kwargs(self.intervention.duration)
#                 )
#                 # lets try again...
#                 return self.inside_intervention()
#             return is_invalid and following_is_intervention
#         return inside_intervention

#     def inside_intervention_started_today(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         if not self.inside_intervention():
#             return False
#         now = timezone.now()
#         return self.intervention.interval_enum.dt(now) == self.intervention.interval_enum.dt(self.int_expected_start)

#     def outside_intervention_expired_today(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         inside_intervention = self.inside_intervention()
#         if inside_intervention is True or inside_intervention is None:
#             return False
#         now = timezone.now()
#         return self.intervention.interval_enum.dt(now) == self.intervention.interval_enum.dt(self.int_expiration)

#     def validate_expiration(self) -> bool:
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         if not self.res_expected_start or not self.res_survey_exp:
#             raise TypeError("This survey has no res_expected_start or res_survey_exp")
#         return self.intervention.interval_enum.dt(now) < self.intervention.interval_enum.dt(self.res_survey_exp)

#     def calculate_expected_dates(self, previous: "InterventionSurvey", user: User) -> "InterventionSurvey":
#         if self.independent_survey == True:
#             membership = user.interventionmembership_set.get(user=user, intervention=self.intervention)
#             self.res_expected_start = membership.created_at + dt.timedelta(
#                 **self.intervention.interval_enum.get_dt_kwargs(self.launch_at * 7)
#             )
#         if previous.assingment_type != self.assingment_type:
#             self.res_expected_start = previous.res_survey_exp + dt.timedelta(
#                 **self.intervention.interval_enum.get_dt_kwargs(self.intervention.duration)
#             )
#             if self.survey_type == TYPE_CHOICES[1][0]:
#                 self.res_survey_exp = self.res_expected_start + dt.timedelta(
#                     **self.intervention.interval_enum.get_dt_kwargs(self.grace_period)
#                 )
#             else:
#                 self.res_survey_exp = self.res_expected_start + dt.timedelta(
#                     **self.intervention.interval_enum.get_dt_kwargs(self.survey_duration)
#                 )
#         else:
#             self.res_expected_start = previous.res_survey_exp
#             if self.survey_type == TYPE_CHOICES[1][0] and self.assingment_type:
#                 if not self.answered_at:
#                     self.res_survey_exp = previous.res_survey_exp + dt.timedelta(
#                         **self.intervention.interval_enum.get_dt_kwargs(self.grace_period)
#                     )
#                 else:
#                     self.res_survey_exp = previous.res_survey_exp + dt.timedelta(
#                         **self.intervention.interval_enum.get_dt_kwargs(self.grace_period + self.survey_duration)
#                     )
#             else:
#                 # check if we must add plus one
#                 self.res_survey_exp = previous.res_survey_exp + dt.timedelta(
#                     **self.intervention.interval_enum.get_dt_kwargs(self.survey_duration)
#                 )
#                 if not hasattr(self, "mem_group_assignment") or not self.mem_group_assignment:
#                     self.mem_group_assignment = user.interventionmembership_set.get(user=user, intervention=self.intervention).group_assignment
#         return self

#     def following_validate_expidation(self, qs: list["InterventionSurvey"], user: User) -> bool:
#         try:
#             previous = qs[qs.index(self) -1]
#         except ValueError:
#             new_self = [x for x in qs if x.id == self.id][0]
#             previous = qs[qs.index(new_self) -1]
#         is_post_monitor_answered = user.interventionmembership_set.get(intervention=self.intervention).is_post_monitor_answered
#         if self.is_previous_post_monitor and not is_post_monitor_answered:
#             self = self.calculate_expected_dates(previous, user)
#             return False
#         try:
#             return self.validate_expiration()
#         except TypeError:
#                 # for some reason this survey has no res_expected_start.
#             try:
#                 self = self.calculate_expected_dates(previous, user)
#                 # let's try again...
#                 return self.validate_expiration()
#             except TypeError:
#                 # need to go one back...
#                 return previous.following_validate_expidation(qs, user)
        
#     def following_validate_expidation_recursively(
#         self,
#         qs: list["InterventionSurvey"],
#         user: User,
#         initial_assingment_type: AssignmentType
#     ):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.

#         This method is a recursive implementation of the `following_validate_expidation`
#         method. It is used to validate the expiration of the surveys that follow
#         the current one.
#         """
#         logger.warning('------- RECURSIVE EXPIRATION ------')
#         logger.warning(f"user.username={user.username}")
#         logger.warning(f"original.position=                 {self.position}")
#         logger.warning(f"original.answered_at=              {self.answered_at}")
#         logger.warning(f"original.res_expected_start=       {self.res_expected_start}")
#         logger.warning(f"original.res_survey_exp=           {self.res_survey_exp}")
#         is_post_monitor_answered = user.interventionmembership_set.get(intervention=self.intervention).is_post_monitor_answered
#         if not self.validate_expiration() or self.is_previous_post_monitor and not is_post_monitor_answered:
#             try:
#                 further_next = qs[qs.index(self) + 1]
#             except IndexError:
#                 logger.warning('------- LAST SURVEY ------')
#                 membership = user.interventionmembership_set.get(user=user, intervention=self.intervention)
#                 logger.warning(f"membership.group_assignment={membership.group_assignment}")
#                 if membership.group_assignment == 'a':
#                     return '/'
#                 else:
#                     return None
#             if further_next.following_validate_expidation(qs, user):
#                 if further_next.assingment_type_enum != initial_assingment_type:
#                     redirect_survey = None
#                 else:
#                     redirect_survey = further_next
#             elif self.inside_intervention_empty_surveys(further_next):
#                 membership = user.interventionmembership_set.get(user=user, intervention=self.intervention)
#                 if membership.group_assignment == 'a':
#                     return None
#                 return '/'
#             else:
#                 return further_next.following_validate_expidation_recursively(qs, user, initial_assingment_type)
#         redirect_survey = further_next
#         logger.warning(f"redirect_survey.position=          {redirect_survey.position if redirect_survey else redirect_survey}")
#         logger.warning(f"redirect_survey.res_expected_start={redirect_survey.res_expected_start if redirect_survey else redirect_survey}")
#         logger.warning(f"redirect_survey.res_survey_exp=    {redirect_survey.res_survey_exp if redirect_survey else redirect_survey}")
#         if redirect_survey is None:
#             return None
#         if self.inside_intervention_empty_surveys(redirect_survey):
#             return None
#         return redirect_survey.get_redirect_url()

#     def is_first_pre_intervention_standard_survey(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         if (
#             self.survey_type == TYPE_CHOICES[0][0]
#             and self.assingment_type == InterventionSurvey.AssignmentType.PRE_INTERVENTION
#             and self.position == 0
#         ):
#             return True
#         return False

#     def is_standard_about_to_expire(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         interv: Intervention = self.intervention
#         return all([
#             self.survey_type == TYPE_CHOICES[0][0],
#             self.answered_at is None,
#             (
#                 interv.interval_enum.dt(self.res_survey_exp) - interv.interval_enum.dt(now)
#                 == dt.timedelta(**interv.interval_enum.get_dt_kwargs(self.pre_expiration_reminder))
#             ),
#         ])

#     def is_monitor_about_to_expire(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         return all([
#             self.survey_type == TYPE_CHOICES[1][0],
#             self.intervention.interval_enum.dt(self.res_survey_exp) - self.intervention.interval_enum.dt(now)
#             == dt.timedelta(**self.intervention.interval_enum.get_dt_kwargs(self.pre_expiration_reminder)),
#         ])

#     def survey_monitor_grace_period_expiration(self, expiration_type: str="COMPLETE"):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         It's important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         if expiration_type == "ALMOST":
#             grace_period = int(self.grace_period / 2)
#             comparison_operator = operator.eq
#         elif expiration_type == "COMPLETE":
#             grace_period = int(self.grace_period)
#             comparison_operator = operator.lt
#         else:
#             assert expiration_type == "TODAY"
#             grace_period = int(self.grace_period)
#             comparison_operator = operator.eq
#         return all([
#             self.survey_type == TYPE_CHOICES[1][0],
#             self.answered_at is None,
#             comparison_operator(
#                 self.intervention.interval_enum.dt(self.res_expected_start)
#                 + dt.timedelta(**self.intervention.interval_enum.get_dt_kwargs(int(grace_period))),
#                 self.intervention.interval_enum.dt(now)
#             ),
#         ])

#     def get_monitor_grace_period_dt(self):
#         return self.intervention.interval_enum.dt(self.res_expected_start) + dt.timedelta(
#             **self.intervention.interval_enum.get_dt_kwargs(self.grace_period)
#         )

#     def is_monitor_grace_period_about_to_expire(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         It's important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         return self.survey_monitor_grace_period_expiration(expiration_type="ALMOST")

#     def is_monitor_grace_period_expired(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` methods.
#         It's important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         return self.survey_monitor_grace_period_expiration()

#     def is_monitor_grace_period_expiring_today(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` methods.
#         It's important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         return self.survey_monitor_grace_period_expiration(expiration_type="TODAY")

#     def expired_today(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         interv: Intervention = self.intervention
#         if self.survey_type == TYPE_CHOICES[1][0]:
#             return all([
#                 interv.interval_enum.dt(self.res_survey_exp) == interv.interval_enum.dt(now)
#             ])
#         else:
#             return all([
#                 self.answered_at is None,
#                 interv.interval_enum.dt(self.res_survey_exp) == interv.interval_enum.dt(now)
#             ])

#     def survey_starts_today(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` methods.
#         It's important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         interv: Intervention = self.intervention
#         return all([
#             interv.interval_enum.dt(self.res_expected_start) == interv.interval_enum.dt(now)
#         ])

#     def is_monitor_inside_duration(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = timezone.now()
#         if (
#             self.survey_type == TYPE_CHOICES[1][0]
#             and self.answered_at is not None
#             and now <= self.answered_at + dt.timedelta(
#                         **self.intervention.interval_enum.get_dt_kwargs(self.survey_duration)
#                     )
#         ):
#             return True
#         return False

#     def is_redirect_candidate(self):
#         """
#         This method assumes that the instance was obtained either using the
#         `get_intervention_map` or `get_empty_intervention_surveys` method.
#         Its important to note that this method will raise an `AttributeError`
#         exception otherwise.
#         """
#         now = self.intervention.interval_enum.dt(timezone.now())
#         dt_kwargs = {
#             "second": 0,
#             "microsecond": 0
#         }
#         if self.intervention.interval_enum == self.intervention.InterventionSurveyIntervals.MINUTES:
#             now = now.replace(**dt_kwargs)
#         if self.answered_at is None:
#             return True
#         elif (
#             self.survey_type == TYPE_CHOICES[1][0]
#             and self.answered_at is not None
#             and now <= self.intervention.interval_enum.dt(
#                 (self.answered_at + dt.timedelta(
#                     **self.intervention.interval_enum.get_dt_kwargs(self.survey_duration)
#                 )).replace(**dt_kwargs)
#             )
#         ):
#             return True
    
#     def get_redirect_url(self):
#         return f"/{self.intervention.slug}/survey/{self.slug}"

#     def get_following_or_intervention_url(self, following: "InterventionSurvey") -> str | None:
#         if self.survey_type == TYPE_CHOICES[1][0] and following.assingment_type != self.assingment_type:
#             return None
#         return following.get_redirect_url()

#     def get_absolute_url(self):
#         return reverse('intervention:survey_detail', args=[str(self.slug)])

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = get_unique_slug(self, 'title', 'slug')
#         super().save(*args, **kwargs)

# SURVEY_QUESTION_TYPE_CHOICES = (
#     ("paragraph", "Paragraph"),
#     ("short answer", "Short Answer"),
#     ("multiple choice", "Multiple Choice"),
#     ("scale", "Scale (0-4)"),
#     ("scale header", "Scale Header: Confidence"),
#     ("scale header agree", "Scale Header: Agree/Disagree"),
#     ("time", "Time in hour and minute"),
#     ("days","Days out of X"),
#     ("height","Height in feet and inches"),
#     ("break", "Multistep Break")
# )
# class SurveyQuestion(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length = 128, default = '', blank=True)
#     export_code = models.CharField(max_length = 12, default = '', blank=True)
#     description = QuillField(blank=True)
#     is_active = models.BooleanField(default=False)
#     survey_assignment = models.ForeignKey('InterventionSurvey', on_delete=models.CASCADE, blank=True, null=True)
#     question_type = models.CharField(max_length = 20, choices = SURVEY_QUESTION_TYPE_CHOICES, default = 'short answer')
#     required = models.BooleanField(default= False)
#     group = MultiSelectField('Group Type', choices=GROUP_CHOICES, max_length=20, default=['a', 'b'])

#     class Meta:
#         ordering = ['position']

#     def __str__(self):
#         return self.title

# class SurveyChoice(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     choice = models.CharField(max_length=5000)
#     question_assignment = models.ForeignKey('SurveyQuestion', on_delete=models.CASCADE, blank=True, null=True)

#     class Meta:
#         ordering = ['position']

# class SurveyAnswer(models.Model):
#     answer = models.CharField(max_length=5000)
#     answer_to = models.ForeignKey(SurveyQuestion, on_delete = models.CASCADE ,related_name = "answer_to")

# class SurveyResponses(models.Model):
#     response_to = models.ForeignKey(InterventionSurvey, on_delete = models.CASCADE, related_name = "survey_response_to")
#     created_at = models.DateTimeField(null=True, blank=True)
#     responder = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "survey_responder", blank = True, null = True)
#     response = models.ManyToManyField(SurveyAnswer, related_name = "survey_response")

# ##################
# ##################
# ##################

# class InterventionScreen(models.Model):
#     title = models.CharField(max_length=128)
#     intervention = models.OneToOneField(Intervention, on_delete=models.CASCADE)
#     description = QuillField(blank=True)
#     success_message = QuillField(blank=True)
#     fail_message = QuillField(blank=True)
#     consent_pdf = models.URLField(max_length=255, default="")

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("intervention:intervention_screen_detail", kwargs={
#             "intervention_slug": self.intervention.slug
#         })

# SCREEN_QUESTION_TYPE_CHOICES = (
#     ("paragraph", "Paragraph"),
#     ("short answer", "Short Answer"),
#     ("multiple choice", "Multiple Choice"),
#     ("eligibility", "Eligibility Screen"),
#     ("height","Feet and inches")
# )

# class ScreenQuestion(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length = 128, default = '')
#     description = QuillField(blank=True)
#     is_active = models.BooleanField(default=False)
#     intervention_screen_assignment = models.ForeignKey('InterventionScreen', on_delete=models.CASCADE, blank=True, null=True)
#     question_type = models.CharField(max_length = 20, choices = SCREEN_QUESTION_TYPE_CHOICES, default = 'short answer')

#     class Meta:
#         ordering = ['position']

#     def __str__(self):
#         return self.title

# class ScreenChoice(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     choice = models.CharField(max_length=5000)
#     question_assignment = models.ForeignKey('ScreenQuestion', on_delete=models.CASCADE, blank=True, null=True)

#     class Meta:
#         ordering = ['position']

# class ScreenAnswer(models.Model):
#     answer = models.CharField(max_length=5000)
#     answer_to = models.ForeignKey(ScreenQuestion, on_delete = models.CASCADE , related_name = "answer_to")

# class ScreenResponses(models.Model):
#     response_to = models.ForeignKey(InterventionScreen, on_delete = models.CASCADE, related_name = "screen_response_to")
#     responder = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "screen_responder", blank = True, null = True)
#     response = models.ManyToManyField(ScreenAnswer, related_name = "screen_response")

# ##################
# ##################
# ##################

# class InterventionMembership(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     # remove null=True
#     intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
#     user = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(default=timezone.now)
#     height_feet = models.CharField(max_length=1, blank=True, null=True)
#     height_inches = models.CharField(max_length=2, blank=True, null=True)
#     weight = models.CharField(max_length=3, blank=True, null=True)
#     has_device = models.BooleanField(default=False)
#     no_compete = models.BooleanField(default=False)
#     has_intervention_access = models.BooleanField(default=False)
#     physical_activity_monitor = models.BooleanField(default=False)
#     will_respond = models.BooleanField(default=False)
#     consent = models.BooleanField(default=False)
#     activated_at = models.DateTimeField(blank=True, null=True)
#     group_assignment = models.CharField(max_length = 1)
#     is_pre_monitor_answered = models.BooleanField(default=False)
#     is_post_monitor_answered = models.BooleanField(default=False)


# class Component(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length=128)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)
#     description = QuillField(blank=True)
#     is_active = models.BooleanField(default=False)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(default=timezone.now)
#     intervention_assignment = models.ForeignKey('Intervention', on_delete=models.CASCADE, blank=True, null=True)

#     class Meta:
#         ordering = ['position']

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("intervention:component_detail", kwargs={
#             "intervention_slug": self.intervention_assignment.slug,
#             "slug": self.slug
#         })

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = get_unique_slug(self, 'title', 'slug' )
#         super().save(*args, **kwargs) 

# class Challenge(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length=128)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)
#     description = QuillField(blank=True)
#     is_active = models.BooleanField(default=False)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(default=timezone.now)
#     component_assignment = models.ForeignKey('Component', on_delete=models.CASCADE, blank=True, null=True)

#     class Meta:
#         ordering = ['position']

#     def __str__(self):
#         return self.title

#     def get_absolute_url(self):
#         return reverse("intervention:challenge_detail", kwargs={
#             "intervention_slug": self.component_assignment.intervention_assignment.slug, 
#             "component_slug": self.component_assignment.slug,
#             "slug": self.slug
#         })

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = get_unique_slug(self, 'title', 'slug' )
#         super().save(*args, **kwargs) 

# PROMPT_TYPE_CHOICES = (
#     ("paragraph", "Paragraph"),
#     ("short answer", "Short Answer"),
#     ("multiple choice", "Multiple Choice"),
#     ("scale", "Scale (0-4)"),
#     ("scale header", "Scale Header"),
# )
# class Responses(models.Model):
#     response_to = models.ForeignKey(Challenge, on_delete = models.CASCADE, related_name = "response_to")
#     responder = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "responder", blank = True, null = True)


# class Prompt(models.Model):
#     position = models.PositiveIntegerField(default=0, blank=False, null=False,)
#     title = models.CharField(max_length = 128, default = '', blank=True)
#     description = QuillField(blank=True)
#     is_active = models.BooleanField(default=False)
#     challenge_assignment = models.ForeignKey('Challenge', on_delete=models.CASCADE, blank=True, null=True)
#     prompt_type = models.CharField(max_length = 20, choices = PROMPT_TYPE_CHOICES, default = 'short answer')

#     class Meta:
#         ordering = ['position']

#     def __str__(self):
#         return self.title


class Answer(models.Model):
    answer = models.CharField(max_length=5000)
    answer_to = models.ForeignKey(Prompt, on_delete=models.CASCADE ,related_name="answer_to")
    response = models.ForeignKey(Responses, on_delete=models.CASCADE)


class Choice(models.Model):
    position = models.PositiveIntegerField(default=0, blank=False, null=False,)
    choice = models.CharField(max_length=5000)
    prompt_assignment = models.ForeignKey(Prompt, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['position']

class ChoiceAnswer(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE , related_name="choice_answer")
    response = models.ForeignKey(Responses, on_delete=models.CASCADE, related_name="response")


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Progress Statistics"
