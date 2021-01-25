import os, config, shutil
import diff_match_patch as dmp_module
from equiv_check import *

# 待处理文件
fn = '1.java'

conf = config.load_config()
dmp = dmp_module.diff_match_patch()

def readfile(fn):
    with open(fn) as f:
        return f.read()

def get_mutants_code(fn):
    cmd = 'bash -c \"%s/javac -XMutator:ALL %s -J-Dmajor.export.mutants=true\"'
    if os.path.exists('mutants'):
        shutil.rmtree('mutants')
    os.system(cmd % (conf.major_path, fn))

def get_patch(f1, f2):
    s1, s2 = readfile(f1), readfile(f2)
    diff = dmp.diff_main(s1, s2)
    p = dmp.patch_make(diff)
    return p

def get_merged_mutant(fn, mutant_num_list):
    text = readfile(fn)
    for mutant_num in mutant_num_list:
        mutant_fn = './mutants/%d/%s' % (mutant_num, fn)
        patch = get_patch(fn, mutant_fn)
        text, result = dmp.patch_apply(patch, text)
    return text

if __name__ == '__main__':
    get_mutants_code(fn)

    mutants_cnt = len(os.listdir('./mutants'))

    test_cases = []
    selected_mutants = []
    ans_code = cur_code = readfile(fn)

    print('STD:')
    print(ans_code + '\n')

    while True:
        flag_new_mutant = False
        for mutant_num in range(1, mutants_cnt + 1):
            # 找到一个 first order mutant，整合进现在的代码，使得它
            if mutant_num in selected_mutants:
                continue
            mutant_fn = './mutants/%d/%s' % (mutant_num, fn)
            tmp_patch = get_patch(fn, mutant_fn)
            tmp_code, _ = dmp.patch_apply(tmp_patch, cur_code)

            print()
            print('Selected mutants:', selected_mutants)
            print('Trying adding new mutant:', mutant_num)
            print('Temp code:\n')
            print(tmp_code + '\n')

            if not check_java_code_equiv(tmp_code, ans_code):
                flag = True
                # 新的代码需要能 pass 之前所有玩家给出的 test case
                for test_case in test_cases:
                    if not check_java_code_equiv_on_case(tmp_code, ans_code, test_case):
                        flag = False
                        break
                if flag:
                    flag_new_mutant = True
                    selected_mutants += [mutant_num]
                    cur_code = tmp_code
                    break

        print('Selected mutants:', selected_mutants)

        print('Current code:')
        print(cur_code + '\n')
                
        if not flag_new_mutant:
            # 找不到新的满足要求的 mutant，玩家胜利
            print('You win!')
            break

        # 找到了新的 mutant，玩家需要给出新的 test case，kill 掉最新的代码
        while True:
            new_test_case = input('Please give a new test case:\n')
            if not check_java_code_equiv_on_case(cur_code, ans_code, new_test_case):
                print("OK!")
                test_cases += [new_test_case]
                break
            print('Nope.')
        
    