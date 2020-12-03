import basic_test
import test_textrank, test_rake_textrank_combo, test_rake

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
    print(test_textrank.get_textrank_results([file]))
    print(textrank.calc_success_rate())
    

main()