import basic_test
import test_textrank, test_rake_textrank_combo, test_rake
import test_TF_IDF

def main():
    # Textrank, textrank + summary, textrank + rake, rake
    file = open("test_vacature.txt", "r", encoding="utf8").read()
    ans = ["informatietechnologie", "netwerkbeheerder", "ict", "specialist", "it", "infrastructuur", 
            "netwerkbeheer", "netwerk", "security", "systeembeheergerelateerde", "databasebeheer", "systeem", "netwerk", 
            "applicatie", "beveiligingsprotocollen", "hbo", "ccna", "mcsa", "linux", "lan", "wan", "infrastructuren",
            "itil", "ids", "ips", "siem", "2fa", "vmware", "prtg", "centos", "windows", "firewalls", 
            "pki", "nederlandse", "nationaliteit", "nederlands", "analytisch", "creatieve", "zelfstandig", "teamverband", 
            "organiseren", "verantwoordelijkheidsgevoel", "fulltime", "rijksoverheid", "projectmanagement", "informatietechniek"]
    
    textrank = basic_test.test(test_textrank.get_textrank_results, [file], ans)
    textrank.run_algorithm()
    textrank.get_test_results(0.5, 1, True)

    textrank_plus = basic_test.test(test_textrank.get_summarised_textrank_results, [file], ans)
    textrank_plus.run_algorithm()
    textrank_plus.get_test_results(0.5, 1, True)

    textrank_rake = basic_test.test(test_rake_textrank_combo.get_combo_results, [file], ans)
    textrank_rake.run_algorithm()
    textrank_rake.get_test_results(0.5, 1, True)

    rake = basic_test.test(test_rake.get_rake_results, [file], ans)
    rake.run_algorithm()
    rake.get_test_results(0.5, 1, True)
    

main()