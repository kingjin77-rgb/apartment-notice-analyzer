const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,AlignmentType,HeadingLevel,BorderStyle,ShadingType,PageOrientation}=require('docx');
const fs=require('fs');
const D=JSON.parse(fs.readFileSync('/tmp/lc/findings.json','utf8'));
const ALL=D.categories.flatMap(c=>c.findings.map(f=>({...f,cat:c.title})));
const ord={'치명':0,'높음':1,'중간':2};
ALL.sort((a,b)=>ord[a.grade]-ord[b.grade]);
const NAVY='1F3864', GOLD='C89B3C', RED='C0392B';
const F='맑은 고딕';

const p=(text,o={})=>new Paragraph({alignment:o.align,spacing:{before:o.before??0,after:o.after??120,line:o.line??300},
  indent:o.indent, border:o.border,
  children:[new TextRun({text,bold:o.b,size:o.size??20,color:o.color??'1A1A1A',font:F})]});

const cellW=[560,700,900,7280];
const TW=cellW.reduce((a,b)=>a+b,0);
const th=t=>new TableCell({width:{size:cellW[0],type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:NAVY},
  margins:{top:60,bottom:60,left:90,right:90},
  children:[new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:t,bold:true,size:18,color:'FFFFFF',font:F})]})]});
const tc=(children,w)=>new TableCell({width:{size:w,type:WidthType.DXA},margins:{top:70,bottom:70,left:100,right:100},children});

const rows=[new TableRow({tableHeader:true,children:[
  ['연번',cellW[0]],['등급',cellW[1]],['근거 면',cellW[2]],['요구사항',cellW[3]]].map(([t,w])=>
  new TableCell({width:{size:w,type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:NAVY},margins:{top:70,bottom:70,left:100,right:100},
    children:[new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:t,bold:true,size:18,color:'FFFFFF',font:F})]})]}))
})];

ALL.forEach((f,i)=>{
  rows.push(new TableRow({children:[
    tc([new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:String(i+1),bold:true,size:18,font:F})]})],cellW[0]),
    tc([new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:f.grade,bold:true,size:18,color:f.grade==='치명'?RED:(f.grade==='높음'?'B7791F':NAVY),font:F})]})],cellW[1]),
    tc([new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:f.pages.join('·')+'면',size:18,font:F})]})],cellW[2]),
    tc([
      new Paragraph({spacing:{after:60},children:[new TextRun({text:f.title,bold:true,size:19,color:NAVY,font:F})]}),
      new Paragraph({spacing:{after:60},children:[new TextRun({text:'[공고문 원문] "'+f.quote+'"',size:16,color:'666666',italics:true,font:F})]}),
      new Paragraph({spacing:{after:60},children:[new TextRun({text:'[검토의견] '+f.problem,size:17,font:F})]}),
      new Paragraph({spacing:{after:60},children:[new TextRun({text:'[정량] '+f.quant,size:17,color:'8A6D1F',font:F})]}),
      new Paragraph({spacing:{after:0},children:[new TextRun({text:'[요구사항] '+f.ask,size:17,bold:true,color:NAVY,font:F})]}),
    ],cellW[3]),
  ]}));
});

const doc=new Document({
  creator:'법무법인 제이엘',title:'번영로 롯데캐슬 센트럴스카이 개선요구서',
  sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1100,bottom:1100,left:900,right:900}}},children:[
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:60},children:[new TextRun({text:'번영로 롯데캐슬 센트럴스카이 입주예정자협의회',bold:true,size:22,color:NAVY,font:F})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:300},border:{bottom:{style:BorderStyle.SINGLE,size:12,color:GOLD,space:6}},children:[new TextRun({text:'자문 : 법무법인 제이엘 분양공고문 분석팀',size:18,color:'666666',font:F})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:200,after:320},children:[new TextRun({text:'입주자모집공고 관련 개선요구 및 질의',bold:true,size:34,color:NAVY,font:F})]}),

    p('수     신 : ㈜무궁화신탁(시행수탁자), 시행위탁자, 롯데건설㈜(시공사)',{size:19}),
    p('참     조 : 분양사업팀, 공사관리팀, 감리단',{size:19}),
    p('제     목 : 「번영로 롯데캐슬 센트럴스카이」 입주자모집공고 검토에 따른 개선요구 및 질의의 건',{size:19,after:220}),

    p('1. 귀사의 무궁한 발전을 기원합니다.',{size:19}),
    p('2. 본 협의회는 「번영로 롯데캐슬 센트럴스카이」(울산광역시 중구 학산동 167-4 일원, 총 634세대) 입주자모집공고 전문 69면을 법무법인 제이엘에 의뢰하여 전수 검토하였습니다. 검토는 공고문 전 면을 5개 구간으로 나누어 통독하는 방식으로 진행하였으며, 미통독 면은 없습니다.',{size:19}),
    p('3. 검토 결과 아래와 같이 총 '+ALL.length+'건의 개선요구 및 질의사항을 도출하였습니다. 각 항목은 모두 공고문 원문 기재사항에 근거하며, 금액·세대수·기간은 공고문 원문과 재대조하여 산출하였습니다.',{size:19}),
    p('4. 각 항목에 대하여 서면으로 회신하여 주시기 바라며, 특히 「치명」 등급 항목은 계약체결 이전에 정정공고 또는 서면 확약이 필요한 사항임을 알려드립니다.',{size:19,after:260}),

    new Table({columnWidths:cellW,width:{size:TW,type:WidthType.DXA},rows}),

    new Paragraph({spacing:{before:320,after:120},children:[new TextRun({text:'회신 요청사항',bold:true,size:22,color:NAVY,font:F})]}),
    p('가. 위 각 항목에 대한 수용 여부와 그 사유를 항목별로 구분하여 서면 회신 바랍니다.',{size:19}),
    p('나. 수용이 어려운 항목은 그 법적·기술적 근거를 함께 제시하여 주시기 바랍니다.',{size:19}),
    p('다. 정정공고가 필요한 항목(주차 관련 표기 충돌, 9인 이상 가구 소득기준 산정 각주, 총 주차대수 미기재 등)은 정정 예정일을 명시하여 주시기 바랍니다.',{size:19}),
    p('라. 회신 기한 : 본 공문 수신일로부터 14일 이내',{size:19,after:260}),

    new Paragraph({spacing:{before:200,after:120},children:[new TextRun({text:'붙임',bold:true,size:22,color:NAVY,font:F})]}),
    p('1. 입주자모집공고 69면 전수 검토보고서 1부.',{size:19}),
    p('2. 동·호수별 유의사항 매트릭스(101·102·103동) 1부.',{size:19}),
    p('3. 층별 공급금액·세대수 대조표(7·8면 기준) 1부.  끝.',{size:19,after:400}),

    new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:400,after:60},children:[new TextRun({text:'번영로 롯데캐슬 센트럴스카이 입주예정자협의회',bold:true,size:24,font:F})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:0},children:[new TextRun({text:'회장               (인)',size:20,font:F})]}),
    new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:260,after:0},children:[new TextRun({text:'※ 본 문서는 입주자모집공고 원문 기재사항에 근거한 검토의견이며, 개별 세대의 계약 판단을 대신하지 않습니다.',size:15,color:'888888',font:F})]}),
  ]}]
});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('/tmp/lc/번영로롯데캐슬_입주예정자협의회_개선요구서.docx',b);console.log('ok',b.length);});
