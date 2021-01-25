import os, re, config
from subprocess import run, PIPE

conf = config.load_config()

if not os.path.exists('temp'):
    os.mkdir('temp')

def readfile(fn):
    with open(fn) as f:
        return f.read()

def check_csharp_code_equiv(c1, c2):
    # Generate wrapper code
    wrapper_template = readfile('template/pex_wrapper_template.cs')

    method_name = c1[:c1.find('(')].strip().split()[-1]
    # print('method name: \''+ method_name + '\'')

    method_arg_list = c1[c1.find('(') + 1: c1.find(')')].split(',')
    method_arg_list = [' '.join(s.strip().split()) for s in method_arg_list]
    # print('method args: ' + str(method_arg_list))

    method_arg_list_untyped = [s.split()[-1] for s in method_arg_list]
    # print('method args (untyped): ' + str(method_arg_list_untyped))

    c2 = c2.replace(method_name + '(', method_name + '_mutated(')

    c1 = c1[c1.find('{') + 1: c1.rfind('}')]
    c2 = c2[c2.find('{') + 1: c2.rfind('}')]

    wrapper_code = wrapper_template.format(
        ', '.join(method_arg_list), 
        method_name, 
        method_name + '_mutated', 
        ', '.join(method_arg_list_untyped), 
        c1, c2
    )

    with open('temp/temp.cs', 'w') as f:
        f.write(wrapper_code)

    # Compile & Run Pex
    print('Compiling wrapper...')
    cmd_compile = '"%s/csc" /target:library temp/temp.cs /out:temp/temp.dll /r:Microsoft.Pex.Framework.dll,Microsoft.ExtendedReflection.dll /debug:pdbonly' % conf.csc_path
    result = os.popen(cmd_compile).read()
    # print(result)

    print('Running Pex...')
    cmd_pex = '"%s/pex" temp/temp.dll /nor /to=5' % conf.pex_path
    result = os.popen(cmd_pex).read()
    # print(result)

    fail = int(re.findall('\d+(?= failing)', result)[0])
    # print(fail + ' fail')
    return fail == 0

def convert_java_to_csharp(code):
    if not os.path.exists('temp_conv'):
        os.mkdir('temp_conv')
    with open('temp_conv/temp.java', 'w') as f:
        f.write(code)
    
    cmd_conv = '"%s/java" -jar sharpencore-0.0.1-SNAPSHOT-jar-with-dependencies.jar ./temp_conv > nul 2>&1' % conf.java_path
    os.popen(cmd_conv).read()
    return readfile('./..net/temp_conv/temp.cs')

def check_java_code_equiv(c1, c2):
    c1, c2 = [convert_java_to_csharp(c) for c in [c1, c2]]
    return check_csharp_code_equiv(c1, c2)

def check_java_code_equiv_on_case(c1, c2, test_case):
    return get_java_code_result_on_case(c1, test_case) == get_java_code_result_on_case(c2, test_case)

def get_java_code_result_on_case(code, test_case):
    code = code[code.find('{') + 1: code.rfind('}')]
    tmp = readfile('template/input_wrapper_template.java') % code
    with open('temp/temp.java', 'w') as f:
        f.write(tmp)
    cmd = 'javac temp/temp.java'
    os.popen(cmd).read()
    p = run('java Main', cwd='temp/', stdout=PIPE, input=test_case, encoding='ascii')
    # print(p.stdout)
    return p.stdout

if __name__ == '__main__':
    # print('equivalent' if check_csharp_code_equiv(readfile('1.cs'), readfile('2.cs')) else 'non-equivalent')
    # print(get_java_code_result_on_case(readfile('1.java'), '1 2'))
    print(convert_java_to_csharp(readfile('1.java')))