import basic_test
import algorithms.textrank, algorithms.rake_textrank_combo, algorithms.rake
import algorithms.TF_IDF
import algorithms.similarity
import algorithms.baseline


def main():
    # Get algorithm input and desired output
    data = "dataset\\test_vacature.txt"
    file = open(data, "r", encoding="utf8").read()
    ans = ["informatietechnologie", "netwerkbeheerder", "ict", "specialist", "it", "infrastructuur", 
            "netwerkbeheer", "netwerk", "security", "systeembeheergerelateerde", "databasebeheer", "systeem", "netwerk", 
            "applicatie", "beveiligingsprotocollen", "hbo", "ccna", "mcsa", "linux", "lan", "wan", "infrastructuren",
            "itil", "ids", "ips", "siem", "2fa", "vmware", "prtg", "centos", "windows", "firewalls", 
            "pki", "nederlandse", "nationaliteit", "nederlands", "analytisch", "creatieve", "zelfstandig", "teamverband", 
            "organiseren", "verantwoordelijkheidsgevoel", "fulltime", "rijksoverheid", "projectmanagement", "informatietechniek"]
    
    # Baseline
    print("Baseline")
    test_baseline = basic_test.test(algorithms.baseline.get_baseline_results, [file], ans)
    test_baseline.run_algorithm()
    test_baseline.get_test_results(0.5, 1, True)

    # Textrank
    print("Textrank")
    test_textrank = basic_test.test(algorithms.textrank.get_textrank_results, [file], ans)
    test_textrank.run_algorithm()
    test_textrank.get_test_results(0.5, 1, True)

    # Textrank + Summary
    print("Textrank + Summary")
    test_textrank_plus = basic_test.test(algorithms.textrank.get_summarised_textrank_results, [file], ans)
    test_textrank_plus.run_algorithm()
    test_textrank_plus.get_test_results(0.5, 1, True)

    # Textrank + Rake
    print("Textrank + Rake")
    test_textrank_rake = basic_test.test(algorithms.rake_textrank_combo.get_combo_results, [file], ans)
    test_textrank_rake.run_algorithm()
    test_textrank_rake.get_test_results(0.5, 1, True)

    # Rake
    print("Rake")
    test_rake = basic_test.test(algorithms.rake.get_rake_results, [file], ans)
    test_rake.run_algorithm()
    test_rake.get_test_results(0.5, 1, True)

    # TF-IDF
    print("TF-IDF")
    test_tf_idf = basic_test.test(algorithms.TF_IDF.TF_IDF_get_results, [file], ans)
    test_tf_idf.run_algorithm()
    test_tf_idf.get_test_results(0.5, 1, True)

    # Similarity Matrix
    print("Similarity Matrix")
    test_similarity = basic_test.test(algorithms.similarity.generate_summary, algorithms.similarity.read_article(data), ans)
    test_similarity.run_algorithm()
    test_similarity.get_test_results(0.5, 1, True)

    # AI's
    # For testing all the AI's, go to AI/run_all_AI.py
    

main()
