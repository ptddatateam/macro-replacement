sqlscript1 = '''
select SurveyResponse.SurveyResponseId, Cast(Question.QuestionId as varchar) AS Question, ISNULL(QuestionDomainValue.DomainValueText, sqr.ResponseValue) as DomainValueText
   FROM Survey LEFT JOIN SurveyUse ON Survey.SurveyId = SurveyUse.SurveyId 
	  Join SurveyResponse on Survey.SurveyId = SurveyResponse.SurveyId 
	  join QuestionnaireQuestion on Survey.QuestionniareId = QuestionnaireQuestion.QuestionniareId
	LEFT JOIN WorkSite ON Survey.WorkSiteId = WorkSite.WorkSiteId
	LEFT JOIN Address on Worksite.AddressId = Address.AddressId
     JOIN Question on Question.QuestionId = QuestionnaireQuestion.QuestionId
	LEFT JOIN SurveyQuestionDomainResponse on SurveyResponse.SurveyResponseId = SurveyQuestionDomainResponse.SurveyResponseId and Question.QuestionId = SurveyQuestionDomainResponse.QuestionId
	LEFT JOIN SurveyQuestionFreeformResponse sqr ON SurveyResponse.SurveyResponseId = sqr.SurveyResponseId and Question.QuestionId = sqr.QuestionId
	LEFT JOIN QuestionDomainValue on SurveyQuestionDomainResponse.DomainValueId = QuestionDomainValue.DomainValueId
	 WHERE WorkSite.WorkSiteId = 820
	 ORDER BY  Question.QuestionId
'''


# pulls all worksites out
sqlscript3  = '''SELECT  [SummaryAdditionalReportingId]
      ,[ProgramDriveAloneRate]
      ,[ProgramVehicleMilesTraveled]
      ,[ProgramDriveAloneRateAffected]
      ,[ProgramVehicleMilesTraveledAffected]
      ,[ModeTotal]
      ,[ModeAlone]
      ,[ModeMotorcycle]
      ,[ModeCarpool]
      ,[ModeVanpool]
      ,[ModeBike]
      ,[ModeBus]
      ,[ModeTrain]
      ,[ModeWalk]
      ,[ModeTelework]
      ,[ModeCWW]
      ,[ModeBoardedFerry]
      ,[ModeUsedFerryAsWalkOn]
      ,[ModeDNW]
      ,[ModeOvernightBusiness]
      ,[ModeOther]
      ,[PercentDriveAlone]
      ,[PercentCarpool]
      ,[PercentVanpool]
      ,[PercentMotorcycle]
      ,[PercentBike]
      ,[PercentBus]
      ,[PercentRail]
      ,[PercentWalk]
      ,[PercentTelework]
      ,[PercentCWW]
      ,[PercentBoardedFerry]
      ,[PercentUsedFerryAsWalkOn]
      ,[ModeTotalAffected]
      ,[ModeAloneAffected]
      ,[ModeCarpoolAffected]
      ,[ModeVanpoolAffected]
      ,[ModeMotorcycleAffected]
      ,[ModeBikeAffected]
      ,[ModeBusAffected]
      ,[ModeTrainAffected]
      ,[ModeWalkAffected]
      ,[ModeTeleworkAffected]
      ,[ModeCWWAffected]
      ,[ModeBoardedFerryAffected]
      ,[ModeUsedFerryAsWalkOnAffected]
      ,[ModeDNWAffected]
      ,[ModeOvernightBusinessAffected]
      ,[ModeOtherAffected]
      ,[PercentDriveAloneAffected]
      ,[PercentCarpoolAffected]
      ,[PercentVanpoolAffected]
      ,[PercentMotorcycleAffected]
      ,[PercentBikeAffected]
      ,[PercentBusAffected]
      ,[PercentRailAffected]
      ,[PercentWalkAffected]
      ,[PercentTeleworkAffected]
      ,[PercentCWWAffected]
      ,[PercentBoardedFerryAffected]
      ,[PercentUsedFerryAsWalkOnAffected]
      ,[TotalEmployeeCount]
      ,[SurveysDistributedCount]
      ,[ActualSurveysReturnedCount]
      ,[ModeMotorcycle1]
      ,[ModeMotorcycle2]
      ,[ModeCarpool2]
      ,[ModeCarpool3]
      ,[ModeCarpool4]
      ,[ModeCarpool5]
      ,[ModeCarpoolGreaterThan5]
      ,[ModeVanpoolLessThan5]
      ,[ModeVanpool5]
      ,[ModeVanpool6]
      ,[ModeVanpool7]
      ,[ModeVanpool8]
      ,[ModeVanpool9]
      ,[ModeVanpool10]
      ,[ModeVanpool11]
      ,[ModeVanpool12]
      ,[ModeVanpool13]
      ,[ModeVanpool14]
      ,[ModeVanpool15]
      ,[ModeMotorcycle1Affected]
      ,[ModeMotorcycle2Affected]
      ,[ModeCarpool2Affected]
      ,[ModeCarpool3Affected]
      ,[ModeCarpool4Affected]
      ,[ModeCarpool5Affected]
      ,[ModeCarpoolGreaterThan5Affected]
      ,[ModeVanpoolLessThan5Affected]
      ,[ModeVanpool5Affected]
      ,[ModeVanpool6Affected]
      ,[ModeVanpool7Affected]
      ,[ModeVanpool8Affected]
      ,[ModeVanpool9Affected]
      ,[ModeVanpool10Affected]
      ,[ModeVanpool11Affected]
      ,[ModeVanpool12Affected]
      ,[ModeVanpool13Affected]
      ,[ModeVanpool14Affected]
      ,[ModeVanpool15Affected]
      ,[GHGSurveyedEmployeesNoFillIn]
      ,[GHGTotalEmployeesNoFillIn]
      ,[BusAPMSurveyedEmployees]
      ,[TrainAPMSurveyedEmployees]
      ,[FerryAPMSurveyedEmployees]
      ,[WalkAPMSurveyedEmployees]
      ,[BikeAPMSurveyedEmployees]
      ,[IsSampling]
      ,[GoalDriveAloneRateAll]
      ,[GoalVehicleMilesTraveledAll]
      ,[GoalDriveAloneRateAffected]
      ,[GoalVehicleMilesTraveledAffected]
	  ,Worksite.WorkSiteName
	  ,Year(Survey.SurveyCloseDate) AS Date
	  ,Address.StreetName
	  ,Address.ZipCode
	  ,WorkSite.WorkSiteId
	  , WorkSite.CTRIdentificationCode
  FROM [CTRSurvey].[dbo].[SummaryAdditionalReporting] as sar
  JOIN WorkSite On sar.WorkSiteId = WorkSite.WorkSiteId
  JOIN Survey on sar.SurveyId = Survey.SurveyId
  JOIN Address on WorkSite.AddressId = Address.AddressId
  ORDER BY Date'''



sqlscript2 = '''select Address.StreetName as EmployerAddress, Address.ZipCode as EmployerZipcode, Address.WSDOTCityCodeId as EmployerCity, Address.WSDOTCountyCodeId as EmployerCounty, Worksite.JurisdictionId,  WorkSite.CTRIdentificationCode, Worksite.WorkSiteName, Survey.SurveyCloseDate, SurveyResponse.SurveyResponseId
   FROM Survey LEFT JOIN SurveyUse ON Survey.SurveyId = SurveyUse.SurveyId 
	  Join SurveyResponse on Survey.SurveyId = SurveyResponse.SurveyId 
	LEFT JOIN WorkSite ON Survey.WorkSiteId = WorkSite.WorkSiteId
	LEFT JOIN Address on Worksite.AddressId = Address.AddressId
    WHERE WorkSite.WorkSiteId = 820
	 ORDER BY SurveyCloseDate DESC, SurveyResponse.SurveyResponseId DESC ''' # pulls metadata on employer

# dictionary for transforming column names into something somewhat more user friendly
labelcoding = {'1': 'EmploymentStatus',
 '10': 'WS_Fri',
 '100': 'SOVCommuteMotiv_carnecessaryforwork',
 '101': 'SOVCommuteMotiv_commutedistanceistooshort',
 '102': 'SOVCommuteMotiv_Caretaking',
 '103': 'SOVCommuteMotiv_ConvenienceOfCar',
 '104': 'SOVCommuteMotiv_DangerofBikingWalking',
 '105': 'SOVCommuteMotiv_nobikeparking',
 '106': 'SOVCommuteMotiv_Other',
 '107': 'irrelevant',
 '11': 'WS_Sat',
 '12': 'WS_Sun',
 '13': 'WS_nomorningcommute',
 '15': 'TransType_Mon',
 '16': 'TransType_Tue',
 '17': 'TransType_Wed',
 '18': 'TransType_Thu',
 '19': 'TransType_Fri',
 '2': 'NonTemp',
 '20': 'TransType_Sat',
 '21': 'TransType_Sun',
 '22': 'PeopleInVanOrCarpool',
 '23': 'TypicalWeek',
 '24': 'WorkSchedule',
 '25': 'OneWayCommute',
 '26': 'Teleworkinpasttwoweeks',
 '27': 'HowManyTeleworkDaysintwoweeks',
 '28': 'Ferry',
 '29': 'ParkAndRide',
 '3': 'FTE',
 '30': 'PayforParking',
 '31': 'HomeZipCode',
 '33': 'CTRCB_employercar',
 '34': 'CTRCB_transportationduringbreaks',
 '35': 'CTRCB_guaranteedridehome',
 '36': 'CTRCB_flexibleschedulingtomaketransit',
 '37': 'CTRCB_incentives',
 '38': 'CTRCB_subsidyforgivingupparking',
 '39': 'CTRCB_priorityparkingfornonsov',
 '4': 'BeginWorkBetween6and9am',
 '40': 'CTRCB_logisticalhelpinnonsovdriving',
 '41': 'CTRCB_bikeparking',
 '42': 'CTRCB_lockersandshowers',
 '43': 'CTRCB_onsiteservices',
 '44': 'CTRCB_onsitefood',
 '45': 'CTRCB_transitconsult',
 '46': 'CTRCB_morebuses',
 '47': 'CTRCB_infoaboutcommutes',
 '48': 'CTRCB_telework',
 '49': 'CTRCB_securityatparkandrides',
 '50': 'CTRCB_morespacesatparkandrides',
 '51': 'CTRCB_other',
 '53': 'likelytotrycarpool',
 '54': 'likelytotryVAN',
 '55': 'likelytotrybus',
 '56': 'likelytotryTrain',
 '57': 'likelytotryBicycle',
 '58': 'likelytotryWalking',
 '59': 'likelytotryTeleWork',
 '6': 'WS_Mon',
 '60': 'likelytotryCompressed',
 '63': 'irrelevant',
 '64': 'irrelevant',
 '65': 'irrelevant',
 '66': 'irrelevant',
 '67': 'irrelevant',
 '68': 'irrelevant',
 '69': 'irrelevant',
 '7': 'WS_Tue',
 '70': 'irrelevant',
 '73': 'irrelevant',
 '74': 'irrelevant',
 '75': 'irrelevant',
 '8': 'WS_Wed',
 '80': 'SOVRecentDayDidYouPayToPark',
 '82': 'HowOftenDoYouTelework',
 '84': 'NonSOVCommuteMotiv_financialincentives',
 '85': 'NonSOVCommuteMotiv_freesubsidizedtransit',
 '86': 'NonSOVCommuteMotiv_personalhealth',
 '87': 'NonSOVCommuteMotiv_parkingcostorconstraint',
 '88': 'NonSOVCommuteMotiv_savemoney',
 '89': 'NonSOVCommuteMotiv_HOVLane',
 '9': 'WS_Thr',
 '90': 'NonSOVCommuteMotiv_cantelework',
 '91': 'NonSOVCommuteMotiv_cantdrivealone',
 '92': 'NonSOVCommuteMotiv_guaranteedridehome',
 '93': 'NonSOVCommuteMotiv_financialincentivenottopark',
 '94': 'NonSOVCommuteMotiv_preferredcarorvanpoolparking',
 '95': 'NonSOVCommuteMotiv_envirocommbenefits',
 '96': 'NonSovCommuteMotiv_Other',
 '98': 'SOVCommuteMotiv_transitinconvenient',
 '99': 'SOVCommuteMotiv_needmoreinfo'}

countylabels = {34: 'Thurston', 6: 'Clark', 17: 'King', 18:'Kitsap', 21: 'Lewis', 23: 'Mason', 27: 'Pierce', 31: 'Snohomish',
                32: 'Spokane', 37: 'Whatcom', 39: 'Yakima', 8:'Cowlitz', 15: 'Island'}



whatcomworksitescript = '''select SurveyResponse.SurveyResponseId, Question.QuestionText,  QuestionnaireQuestion.QuestionNumber AS Question,ISNULL(cast(QuestionDomainValue.DomainValueId as varchar), cast(sqr.ResponseValue as varchar)) as OtherDomainValueText, QuestionDomainValue.DomainValueText, Worksite.WorkSiteId, Address.StreetName, Address.Zipcode, Survey.SurveyCloseDate
   FROM Survey LEFT JOIN SurveyUse ON Survey.SurveyId = SurveyUse.SurveyId 
	  Join SurveyResponse on Survey.SurveyId = SurveyResponse.SurveyId 
	  join QuestionnaireQuestion on Survey.QuestionniareId = QuestionnaireQuestion.QuestionniareId
	LEFT JOIN WorkSite ON Survey.WorkSiteId = WorkSite.WorkSiteId
	LEFT JOIN Address on Worksite.AddressId = Address.AddressId
     JOIN Question on Question.QuestionId = QuestionnaireQuestion.QuestionId
	LEFT JOIN SurveyQuestionDomainResponse on SurveyResponse.SurveyResponseId = SurveyQuestionDomainResponse.SurveyResponseId and Question.QuestionId = SurveyQuestionDomainResponse.QuestionId
	LEFT JOIN SurveyQuestionFreeformResponse sqr ON SurveyResponse.SurveyResponseId = sqr.SurveyResponseId and Question.QuestionId = sqr.QuestionId
	LEFT JOIN QuestionDomainValue on SurveyQuestionDomainResponse.DomainValueId = QuestionDomainValue.DomainValueId
	 WHERE WorkSite.WorkSiteId in (254,255,256,258,262,265,266,269,270,271,272,273,274,275,279,284,285,287,288,289,291,293,294,295,296)
	 ORDER BY  SurveyResponse.SurveyResponseId'''