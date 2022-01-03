# 리눅스에서만 작동

# 샌드박스는 쥐뿔 시X

import os
import sys
import tempfile
import subprocess


def execute_in_sandbox(code, language, input_str):
    if language == 'python':
        timeout = False

        tmp_fd, tmp_filename = tempfile.mkstemp(suffix='.py')
        os.close(tmp_fd)

        with open(tmp_filename, 'w+') as fd:
            fd.write(code)

        ps = subprocess.Popen(['python', tmp_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        try:
            outs, errs = ps.communicate(bytes(input_str, encoding='utf8'))
            ps.wait(timeout=5)
            

        except subprocess.TimeoutExpired:
            ps.kill()
            outs, errs = ps.communicate() 
            timeout = True

        finally:
            try:
                ps.stdout.close()
                ps.stdin.close()
            except ValueError:
                pass
            return outs.decode('utf-8'), errs.decode('utf-8'), timeout

    elif language == 'c':
        timeout = False

        tmp_fd, tmp_filename = tempfile.mkstemp(suffix='.c')
        os.close(tmp_fd)

        with open(tmp_filename, 'w+') as fd:
            fd.write(code)

        ps = subprocess.Popen(['gcc', tmp_filename, '-o', tmp_filename + '.o'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        try:
            outs, errs = ps.communicate()
            ps.wait()
            
        finally:
            try:
                ps.stdout.close()
                ps.stdin.close()
            except ValueError:
                pass

            if errs:    # 컴파일 에러
                return outs.decode('utf-8'), errs.decode('utf-8'), True
            else:       # 정상 실행

                ps = subprocess.Popen([tmp_filename + '.o'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


                try:
                    outs, errs = ps.communicate(bytes(input_str, encoding='utf8'))
                    ps.wait()
                    

                finally:
                    try:
                        ps.stdout.close()
                        ps.stdin.close()
                    except ValueError:
                        pass

                    if errs:    # 에러
                        return outs.decode('utf-8'), errs.decode('utf-8'), True
                    else:       # 정상 실행
                        return outs.decode('utf-8'), errs.decode('utf-8'), False

    elif language == 'cpp':
        timeout = False

        tmp_fd, tmp_filename = tempfile.mkstemp(suffix='.cc')
        os.close(tmp_fd)

        with open(tmp_filename, 'w+') as fd:
            fd.write(code)

        ps = subprocess.Popen(['g++', tmp_filename, '-o', tmp_filename + '.o'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        try:
            outs, errs = ps.communicate()
            ps.wait()
            
        finally:
            try:
                ps.stdout.close()
                ps.stdin.close()
            except ValueError:
                pass

            if errs:    # 컴파일 에러
                return outs.decode('utf-8'), errs.decode('utf-8'), True
            else:       # 정상 실행

                ps = subprocess.Popen([tmp_filename + '.o'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


                try:
                    outs, errs = ps.communicate(bytes(input_str, encoding='utf8'))
                    ps.wait()
                    

                finally:
                    try:
                        ps.stdout.close()
                        ps.stdin.close()
                    except ValueError:
                        pass

                    if errs:    # 에러
                        return outs.decode('utf-8'), errs.decode('utf-8'), True
                    else:       # 정상 실행
                        return outs.decode('utf-8'), errs.decode('utf-8'), False



# Test
if __name__ == '__main__':
    outs, errs, timeout = (execute_in_sandbox("#include <iostream>\nint main (){std::cout << \"Fuck you\"; return 0;}", 'cpp', ''))
    print(outs)
    print(errs)
    exit(0)