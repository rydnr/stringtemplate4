/*
 [The "BSD license"]
 Copyright (c) 2009 Terence Parr
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
package org.stringtemplate.v4.test;

import org.junit.Test;
import org.stringtemplate.v4.ST;
import org.stringtemplate.v4.STGroup;

import static org.junit.Assert.assertEquals;

public class TestLists extends BaseTest {
	@Test public void testJustCat() throws Exception {
		org.stringtemplate.v4.ST e = new org.stringtemplate.v4.ST(
				"<[names,phones]>"
			);
		e.add("names", "Ter");
		e.add("names", "Tom");
		e.add("phones", "1");
		e.add("phones", "2");
		String expecting = "TerTom12";
		assertEquals(expecting, e.render());
	}

	@Test public void testCat2Attributes() throws Exception {
		org.stringtemplate.v4.ST e = new ST(
				"<[names,phones]; separator=\", \">"
			);
		e.add("names", "Ter");
		e.add("names", "Tom");
		e.add("phones", "1");
		e.add("phones", "2");
		String expecting = "Ter, Tom, 1, 2";
		assertEquals(expecting, e.render());
	}

	@Test public void testCat2AttributesWithApply() throws Exception {
		org.stringtemplate.v4.ST e = new org.stringtemplate.v4.ST(
				"<[names,phones]:{a|<a>.}>"
			);
		e.add("names", "Ter");
		e.add("names", "Tom");
		e.add("phones", "1");
		e.add("phones", "2");
		String expecting = "Ter.Tom.1.2.";
		assertEquals(expecting, e.render());
	}

	@Test public void testCat3Attributes() throws Exception {
		org.stringtemplate.v4.ST e = new org.stringtemplate.v4.ST(
				"<[names,phones,salaries]; separator=\", \">"
			);
		e.add("names", "Ter");
		e.add("names", "Tom");
		e.add("phones", "1");
		e.add("phones", "2");
		e.add("salaries", "big");
		e.add("salaries", "huge");
		String expecting = "Ter, Tom, 1, 2, big, huge";
		assertEquals(expecting, e.render());
	}

    @Test public void testCatWithTemplateApplicationAsElement() throws Exception {
        ST e = new org.stringtemplate.v4.ST(
                "<[names:{<it>!},phones]; separator=\", \">"
            );
        e.add("names", "Ter");
        e.add("names", "Tom");
        e.add("phones" , "1");
        e.add("phones", "2");
        String expecting = "Ter!, Tom!, 1, 2";
        assertEquals(expecting, e.render());
    }

    @Test public void testCatWithIFAsElement() throws Exception {
        ST e = new org.stringtemplate.v4.ST(
                "<[{<if(names)>doh<endif>},phones]; separator=\", \">"
            );
        e.add("names", "Ter");
        e.add("names", "Tom");
        e.add("phones" , "1");
        e.add("phones", "2");
        String expecting = "doh, 1, 2";
        assertEquals(expecting, e.render());
    }

    @Test public void testCatWithNullTemplateApplicationAsElement() throws Exception {
        org.stringtemplate.v4.ST e = new ST(
                "<[names:{<it>!},\"foo\"]:{x}; separator=\", \">"
            );
        e.add("phones", "1");
        e.add("phones", "2");
        String expecting = "x";  // only one since template application gives nothing
        assertEquals(expecting, e.render());
    }

    @Test public void testCatWithNestedTemplateApplicationAsElement() throws Exception {
        ST e = new org.stringtemplate.v4.ST(
                "<[names, [\"foo\",\"bar\"]:{<it>!},phones]; separator=\", \">"
            );
        e.add("names", "Ter");
        e.add("names", "Tom");
        e.add("phones", "1");
        e.add("phones", "2");
        String expecting = "Ter, Tom, foo!, bar!, 1, 2";
        assertEquals(expecting, e.render());
    }

    @Test public void testListAsTemplateArgument() throws Exception {
		String templates =
				"test(names,phones) ::= \"<foo([names,phones])>\""+newline+
				"foo(items) ::= \"<items:{a | *<a>*}>\""+newline
				;
        writeFile(tmpdir, "t.stg", templates);
        STGroup group = new org.stringtemplate.v4.STGroupFile(tmpdir+"/"+"t.stg");
		org.stringtemplate.v4.ST e = group.getInstanceOf("test");
		e.add("names", "Ter");
		e.add("names", "Tom");
		e.add("phones", "1");
		e.add("phones", "2");
		String expecting = "*Ter**Tom**1**2*";
		String result = e.render();
		assertEquals(expecting, result);
	}
}