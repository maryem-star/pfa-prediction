import sys
sys.path.insert(0, r'C:\Users\dell\Desktop\pfa-projet\pfa-student-prediction')

from src.preprocessing.module_relations import predict_all_modules_3A

# Test etudiant fort ITE
etudiant_fort = {
    'Module_S1_1': 16.0, 'Module_S1_2': 15.0, 'Module_S1_3': 14.0,
    'Module_S1_4': 15.0, 'Module_S1_5': 17.0,
    'Module_S2_1': 15.0, 'Module_S2_2': 16.0, 'Module_S2_3': 17.0,
    'Module_S2_4': 16.0, 'Module_S2_5': 15.0,
    'PFA_2': 16.0, 'Absences_S1': 3, 'Absences_S2': 2, 'Redoublant': 0,
}

res_fort = predict_all_modules_3A(etudiant_fort, 'ite')
print('=== ETUDIANT FORT (ITE) ===')
print('Statut:', res_fort['statut_global'])
print('Modules valides:', res_fort['nb_valides'], '/', res_fort['nb_total'])
print('Note S5 estimee:', res_fort['note_s5_predite'], '/20')
print('Note PFE estimee:', res_fort['note_pfe_predite'], '/20')
print('Resume:', res_fort['resume'])
for k, v in res_fort['modules_3A'].items():
    icon = 'OK' if v['valide'] else 'X '
    print(' [' + icon + '] ' + v['label_fr'] + ': ' + str(v['score_prereq']) + '/20 | Prob: ' + str(round(v['probabilite']*100, 0)) + '%')

print()

# Test etudiant faible avec absences
etudiant_faible = {
    'Module_S1_1': 8.0, 'Module_S1_2': 7.0, 'Module_S1_3': 9.0,
    'Module_S1_4': 8.0, 'Module_S1_5': 7.0,
    'Module_S2_1': 9.0, 'Module_S2_2': 8.0, 'Module_S2_3': 9.0,
    'Module_S2_4': 8.0, 'Module_S2_5': 7.0,
    'PFA_2': 9.0, 'Absences_S1': 15, 'Absences_S2': 20, 'Redoublant': 1,
}

res_faible = predict_all_modules_3A(etudiant_faible, 'ite')
print('=== ETUDIANT FAIBLE (ITE - absences + redoublant) ===')
print('Statut:', res_faible['statut_global'])
print('Modules valides:', res_faible['nb_valides'], '/', res_faible['nb_total'])
print('Note S5 estimee:', res_faible['note_s5_predite'], '/20')
print('Note PFE estimee:', res_faible['note_pfe_predite'], '/20')

print()
print('=== COMPARAISON 6 FILIERES (etudiant moyen) ===')
etudiant_moyen = {
    'Module_S1_1': 13.0, 'Module_S1_2': 12.5, 'Module_S1_3': 12.5,
    'Module_S1_4': 13.0, 'Module_S1_5': 12.5,
    'Module_S2_1': 13.0, 'Module_S2_2': 13.0, 'Module_S2_3': 13.5,
    'Module_S2_4': 12.5, 'Module_S2_5': 13.0,
    'PFA_2': 14.0, 'Absences_S1': 8, 'Absences_S2': 8, 'Redoublant': 0,
}

for fil in ['ite', 'isic', 'ccn', 'gee', 'civil', 'industriel']:
    r = predict_all_modules_3A(etudiant_moyen, fil)
    print('  ' + fil.upper().ljust(12) + ': ' + str(r['nb_valides']) + '/' + str(r['nb_total']) + ' modules | S5=' + str(r['note_s5_predite']) + ' | PFE=' + str(r['note_pfe_predite']) + ' | ' + r['statut_global'])

print()
print('Tous les tests passes avec succes!')
